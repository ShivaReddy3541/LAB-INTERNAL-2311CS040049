# Project 06 — AI Policy & Compliance Governance Engine

> **Hybrid Rule & LLM Corporate Expense Governance Powered by Google Gemini 2.5 Flash**

---

## 🎯 Overview

The **AI Policy & Compliance Governance Engine** evaluates corporate expense claims against financial policy rules. It uses a deterministic rule engine to flag maximum transaction limits, restricted merchant categories, and missing receipt requirements, combined with Gemini 2.5 Flash to generate formal executive compliance reports.

---

## 🏗️ Governance Architecture

```
[Expense Claim Request]
          │
          ▼
[Deterministic Policy Rule Engine]
   ├── Max Transaction Limit ($1,000)
   ├── Allowed Expense Categories
   ├── Restricted Merchant Rules
   └── Receipt Threshold Check ($50)
          │
          ▼
[Compliance Determination: COMPLIANT / WARNING / NON_COMPLIANT]
          │
          ▼
[Google Gemini 2.5 Flash Auditor] ──(Fallback)──► [Formal AI Audit Synthesizer]
          │
          ▼
[FastAPI REST API (Port 8006)] ──► [Executive Audit Dashboard]
```

---

## ⚡ Key Features

- **Hybrid Audit Architecture**: Combines zero-error deterministic financial rules with LLM narrative summaries.
- **Formal Audit Reports**: Generates detailed 2-sentence executive determinations explaining compliance decisions.
- **Human Review Flagging**: Automatically flags `NON_COMPLIANT` and `WARNING` claims for human oversight.
- **Audit Dashboard**: Real-time violation badges, expense breakdowns, and policy documentation.

---

## 🔌 API Endpoints Specification

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Serves the Policy Compliance UI. |
| `GET` | `/api/policies` | Returns corporate policy rules and threshold definitions. |
| `POST` | `/api/audit-claim` | Audits an expense claim and returns violations, status, and AI summary. |

---

## 🚀 Running Standalone Server

To run Project 06 standalone on port `8006`:

```bash
cd 06_policy_compliance/src
python -m uvicorn server:app --host 127.0.0.1 --port 8006
```

Access the UI at: **http://127.0.0.1:8006**

---

## 🧪 Automated Testing

Run unit tests for Project 06:

```bash
python -m pytest 06_policy_compliance/tests/
```
