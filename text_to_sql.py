import os
import json
import time
import numpy as np
from dotenv import load_dotenv
from google import genai
from google.genai import types

from database import execute_query

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Primary model from .env
GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite"
)

# Backup models in case the primary model temporarily returns 503
FALLBACK_MODELS = [
    GEMINI_MODEL,
    "gemini-3.6-flash",
    "gemini-3.7-flash",
    "gemini-3.8-flash",
]

GEMINI_EMBEDDING_MODEL = os.getenv(
    "GEMINI_EMBEDDING_MODEL",
    "gemini-embedding-001"
)

SCHEMA_INDEX_PATH = os.getenv(
    "SCHEMA_INDEX_PATH",
    "data/schema_index.json"
)

client = genai.Client(api_key=GEMINI_API_KEY)

_schema_records_cache = None


# ---------------------------------------------------------
# LOAD SCHEMA INDEX
# ---------------------------------------------------------

def load_schema_index():
    global _schema_records_cache

    if _schema_records_cache is None:
        if os.path.exists(SCHEMA_INDEX_PATH):
            with open(SCHEMA_INDEX_PATH, "r", encoding="utf-8") as f:
                _schema_records_cache = json.load(f)
        else:
            _schema_records_cache = []

    return _schema_records_cache


# ---------------------------------------------------------
# EMBEDDINGS
# ---------------------------------------------------------

def embed_text(text: str):
    result = client.models.embed_content(
        model=GEMINI_EMBEDDING_MODEL,
        contents=text,
    )

    return result.embeddings[0].values


# ---------------------------------------------------------
# COSINE SIMILARITY
# ---------------------------------------------------------

def _cosine_similarity(a, b):
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)

    denom = np.linalg.norm(a) * np.linalg.norm(b)

    if denom == 0:
        return 0.0

    return float(np.dot(a, b) / denom)


# ---------------------------------------------------------
# LOCAL SCHEMA SEARCH
# ---------------------------------------------------------

def search_index(query_text, top=5):
    """
    Return the top relevant schema records.
    """

    records = load_schema_index()

    if not records:
        return []

    query_embedding = embed_text(query_text)

    scored = [
        (
            _cosine_similarity(
                query_embedding,
                rec["embedding"]
            ),
            rec
        )
        for rec in records
    ]

    scored.sort(
        key=lambda pair: pair[0],
        reverse=True
    )

    return [
        rec
        for _, rec in scored[:top]
    ]


# ---------------------------------------------------------
# BUILD SCHEMA CONTEXT
# ---------------------------------------------------------

def build_schema_context(doc):
    return (
        f"Type: {doc.get('type', '')}\n"
        f"Name: {doc.get('name', '')}\n"
        f"Description: {doc.get('description', '')}\n"
        f"Columns: {doc.get('columns', '')}\n"
        f"Relationships: {doc.get('relationships', '')}\n"
    )


# ---------------------------------------------------------
# CLEAN SQL
# ---------------------------------------------------------

def clean_sql(sql: str):

    if not sql:
        return ""

    lines = sql.strip().splitlines()

    cleaned_lines = [
        line
        for line in lines
        if not line.strip().startswith("```")
    ]

    sql = "\n".join(cleaned_lines).strip()

    # Remove accidental "sql" prefix
    if sql.lower().startswith("sql\n"):
        sql = sql[4:].strip()

    return sql


# ---------------------------------------------------------
# GEMINI SQL GENERATION
# ---------------------------------------------------------

def generate_sql_with_model(question, system_prompt, model):

    response = client.models.generate_content(
        model=model,
        contents=question,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0,
            max_output_tokens=300,
        ),
    )

    return clean_sql(
        response.text or ""
    )


# ---------------------------------------------------------
# QUESTION -> SQL
# ---------------------------------------------------------

def question_to_sql(question: str):

    # Retrieve multiple relevant schema records
    search_results = search_index(
        question,
        top=5
    )

    context_parts = []

    for record in search_results:
        context_parts.append(
            build_schema_context(record)
        )

    context = "\n\n".join(context_parts)

    system_prompt = (
        "You are QueryPilot, a Text-to-SQL assistant.\n\n"

        "Your task is to convert the user's natural language "
        "question into ONE valid, executable MySQL query.\n\n"

        "AVAILABLE TABLES:\n"
        "- customers\n"
        "- suppliers\n"
        "- products\n"
        "- orders\n"
        "- order_details\n\n"

        "RELEVANT DATABASE SCHEMA:\n"
        f"{context}\n\n"

        "STRICT RULES:\n"
        "1. Return ONLY the SQL query.\n"
        "2. Do not return explanations.\n"
        "3. Do not use markdown.\n"
        "4. Do not use code fences.\n"
        "5. Always use valid MySQL syntax.\n"
        "6. Always use a valid FROM clause.\n"
        "7. Use exact table names from the schema.\n"
        "8. Use exact column names from the schema.\n"
        "9. For counting rows, use COUNT(*).\n"
        "10. Never output COUNT by itself.\n"
        "11. Use JOINs when information from multiple tables is required.\n"
        "12. Do not invent tables or columns.\n"
        "13. Return one executable SQL statement only.\n\n"

        "EXAMPLES:\n"

        "Question: find total number of customers\n"
        "SQL: SELECT COUNT(*) FROM customers;\n\n"

        "Question: show all customers\n"
        "SQL: SELECT * FROM customers;\n\n"

        "Question: show the top 5 products by price\n"
        "SQL: SELECT * FROM products ORDER BY price DESC LIMIT 5;\n"
    )

    last_error = None

    # Try each model
    for model in FALLBACK_MODELS:

        # Retry temporary 503 errors twice
        for attempt in range(2):

            try:

                sql = generate_sql_with_model(
                    question,
                    system_prompt,
                    model
                )

                if sql:
                    return sql

            except Exception as e:

                last_error = e

                error_text = str(e)

                # Only retry/fallback for temporary availability errors
                if "503" in error_text or "UNAVAILABLE" in error_text:

                    if attempt == 0:
                        time.sleep(2)
                    else:
                        time.sleep(1)

                    continue

                # For non-503 errors, don't silently hide the problem
                raise e

    raise RuntimeError(
        "Gemini is temporarily unavailable on all configured "
        f"models. Last error: {last_error}"
    )


# ---------------------------------------------------------
# TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    question = (
        "What is the total shipping cost of orders for each country?"
    )

    try:

        sql_query = question_to_sql(question)

        print("\nGenerated SQL:")
        print(sql_query)

        results = execute_query(sql_query)

        print("\nQuery Results:")
        print(results)

    except Exception as e:

        print("\nError:")
        print(e)
