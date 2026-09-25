# QueryPilot

QueryPilot is a Streamlit-based Text-to-SQL application that allows users to query a MySQL database using natural language.

Instead of writing SQL manually, users can simply ask questions such as:

> Find the total number of customers

QueryPilot uses Google Gemini to understand the question, retrieves relevant database schema information using local embeddings, generates a MySQL query, and executes it against the connected database.

## Features

- Natural language to SQL generation
- Gemini-powered SQL generation
- Local schema retrieval using embeddings
- MySQL database integration
- Automatic SQL query execution
- Interactive Streamlit interface
- Query results displayed directly in the application

## How It Works

```text
User Question
      ↓
Gemini Embedding
      ↓
Local Schema Search
      ↓
Relevant Schema Context
      ↓
Gemini
      ↓
Generated MySQL Query
      ↓
MySQL Database
      ↓
Query Results

##Tech Stack

Python
Streamlit – Web interface
Google Gemini API – SQL generation and embeddings
MySQL – Database
NumPy – Similarity calculations
python-dotenv – Environment variable management
```
