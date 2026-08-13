# QueryPilot

QueryPilot is a production-oriented **SQL Analytics RAG Agent** designed to allow users to ask natural-language questions about structured business data. It leverages Retrieval-Augmented Generation (RAG) to inject business context and definitions, generates SQL safely, executes it against a PostgreSQL database, and presents deterministic numerical answers with charts.

## Problem Statement

Traditional "Chat with Database" solutions often fail because LLMs hallucinate SQL queries, misunderstand business definitions (e.g., "Net Revenue" vs "Gross Revenue"), or perform math incorrectly.

## Why RAG is Required

RAG solves this by retrieving explicit business rules, semantic definitions, and database schemas *before* the LLM generates SQL. This ensures the LLM knows *exactly* which tables, columns, and formulas to use for a given natural-language question.

## Architecture

```text
React (Frontend)
  ↓
FastAPI (Backend Orchestrator)
  ↓
Query Understanding (Intent, Dimensions, Filters)
  ↓
Hybrid Retrieval (pgvector + FTS) + RRF + Cross-Encoder Reranker
  ↓
Context Builder (Business Rules + Schema + User Query)
  ↓
LLM (Text-to-SQL Generation)
  ↓
SQL Validator (Syntax, Security & Scope Checks)
  ↓
Supabase PostgreSQL (Deterministic Execution)
  ↓
Pandas / NumPy (Post-processing)
  ↓
React (Answer + Visualization + Sources)
```

## Tech Stack

- **Frontend**: React, Vite, Tailwind CSS, Recharts
- **Backend**: Python, FastAPI, Pydantic, SQLAlchemy, psycopg
- **Database**: Supabase PostgreSQL, pgvector
- **RAG Engine**: Sentence Transformers (BGE Embeddings & Reranker)
- **Data Post-processing**: Pandas, NumPy
- **LLM**: Configurable (Default: Groq)

## Installation & Setup

1. **Clone & Setup Database**
   ```bash
   # Initialize and start local Supabase (Requires Docker)
   npx supabase start
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Limitations & Future Improvements
- **Current Limitation**: Designed primarily for read-only analytical queries.
- **Future Improvements**: Multi-turn conversation awareness, query caching, streaming visualization generation.
