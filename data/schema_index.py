import os
import json
import pandas as pd
from dotenv import load_dotenv

from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_EMBEDDING_MODEL = os.getenv(
    "GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")
SCHEMA_INDEX_PATH = os.getenv("SCHEMA_INDEX_PATH", "data/schema_index.json")
SCHEMA_CSV_PATH = os.getenv(
    "SCHEMA_CSV_PATH", "data/querypilot_vector_schema_info.csv")

client = genai.Client(api_key=GEMINI_API_KEY)


def embed_text(text: str):
    result = client.models.embed_content(
        model=GEMINI_EMBEDDING_MODEL,
        contents=text,
    )
    return result.embeddings[0].values


def build_index():
    df = pd.read_csv(SCHEMA_CSV_PATH)
    df = df.fillna("")

    records = []
    for _, row in df.iterrows():
        doc = {
            "id": str(row["id"]),
            "type": str(row["type"]),
            "name": str(row["name"]),
            "description": str(row["description"]),
            "columns": str(row["columns"]),
        }
        text_for_embedding = f"{doc['name']} {doc['description']} {doc['columns']}"
        doc["embedding"] = embed_text(text_for_embedding)
        records.append(doc)
        print(f"Embedded: {doc['name']}")

    os.makedirs(os.path.dirname(SCHEMA_INDEX_PATH) or ".", exist_ok=True)
    with open(SCHEMA_INDEX_PATH, "w") as f:
        json.dump(records, f)

    print(
        f"[OK] Saved {len(records)} schema records with embeddings to {SCHEMA_INDEX_PATH}")


if __name__ == "__main__":
    build_index()
