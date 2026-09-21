# Project 01 — Real-Time Text-to-SQL AI Studio

> **Natural Language Database Analytics Powered by Google Gemini 2.5 Flash**

---

## 🎯 Overview

The **Real-Time Text-to-SQL AI Studio** transforms natural language questions into safe, executable SQLite queries. It features a live data streaming transaction engine, an interactive Schema Explorer, read-only SQL safety validator, CSV data export, and real-time Server-Sent Events (SSE) AI query explanations.

---

## 🏗️ Architecture

```
[User Natural Query] 
        │
        ▼
[SchemaRetriever & Few-Shot RAG]
        │
        ▼
[Google Gemini 2.5 Flash Generator] ──(Fallback)──► [Intelligent SQL Rule Engine]
        │
        ▼
[SQLValidator (Regex & Read-Only Check)]
        │
        ▼
[SQLite Execution Engine (timeout=30.0s)]
        │
        ▼
[FastAPI REST API & SSE Explainer (Port 8001)] ──► [Glassmorphism Web UI]
```

---

## ⚡ Key Features

- **Gemini 2.5 Flash Translation**: Translates complex natural queries into SQLite syntax.
- **Intelligent SQL Fallback**: Translates queries into SQL even without an API key using schema-mapped heuristics.
- **Read-Only Safety Validator**: Blocks `DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, and non-SELECT statements.
- **Real-Time Order Streaming**: Continuous background simulation adding live e-commerce transactions every 6 seconds.
- **Interactive UI**: Deep Navy glassmorphism visual design, revenue metrics, query chips, and CSV exporter.

---

## 🔌 API Endpoints Specification

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Serves the single-page application UI. |
| `GET` | `/api/schema` | Returns the database schema summary. |
| `GET` | `/api/realtime-stats` | Returns live total revenue, order count, and latest transaction details. |
| `POST` | `/api/query` | Translates natural question to SQL and executes query. |
| `POST` | `/api/simulate-live-order` | Manually triggers a real-time e-commerce transaction. |
| `GET` | `/api/stream-explain` | Streams token-by-token AI SQL explanations via SSE. |

---

## 🚀 Running Standalone Server

To run Project 01 standalone on port `8001`:

```bash
cd 01_text_to_sql/src
python -m uvicorn server:app --host 127.0.0.1 --port 8001
```

Access the UI at: **http://127.0.0.1:8001**

---

## 🧪 Automated Testing

Run unit tests for Project 01:

```bash
python -m pytest 01_text_to_sql/tests/
```
