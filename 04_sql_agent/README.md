# Project 04 — Autonomous SQL ReAct Agent

> **Autonomous Tool-Using Database Agent Powered by Google Gemini 2.5 Flash**

---

## 🎯 Overview

The **Autonomous SQL ReAct Agent** implements the Reasoning + Acting (ReAct) paradigm. The agent dynamically decides which database tools to invoke (`inspect_schema`, `validate_sql`, `run_sql_query`), observes output results, self-corrects invalid queries, and synthesizes answers.

---

## 🏗️ ReAct Agent Loop

```
[User Question]
      │
      ▼
[Thought 1: Inspect database schema]
      │
      ▼
[Action 1: inspect_schema()] ──► [Observation 1: Table & Column Specs]
      │
      ▼
[Thought 2: Formulate SQL query]
      │
      ▼
[Action 2: run_sql_query(sql)] ──► [Observation 2: Execution Results]
      │
      ▼
[Final Answer Synthesis]
```

---

## ⚡ Key Features

- **ReAct Agent Trajectory**: Full visibility into agent thoughts, actions, and observations.
- **Dynamic Schema-Mapped Fallback Engine**: Generates schema-compliant SQL queries via regex rule engine if LLM API key is absent.
- **Strict Word-Boundary Security**: Prevents SQL injection or false positive keyword flags (e.g. `created_at` column selections are permitted).
- **Tool Interoperability**: Seamlessly executes read-only queries against SQLite instances (`agent_db.db`).

---

## 🔌 API Endpoints Specification

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Serves the ReAct SQL Agent UI. |
| `GET` | `/api/schema` | Returns database schema specification. |
| `POST` | `/api/run-agent` | Executes the ReAct agent workflow and returns trajectory logs. |

---

## 🚀 Running Standalone Server

To run Project 04 standalone on port `8004`:

```bash
cd 04_sql_agent/src
python -m uvicorn server:app --host 127.0.0.1 --port 8004
```

Access the UI at: **http://127.0.0.1:8004**

---

## 🧪 Automated Testing

Run unit tests for Project 04:

```bash
python -m pytest 04_sql_agent/tests/
```
