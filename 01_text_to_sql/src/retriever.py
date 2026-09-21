"""Schema and example SQL retriever for Text-to-SQL Workflow."""
import sqlite3
from typing import Dict, List, Any

SAMPLE_FEW_SHOT_EXAMPLES = [
    {
        "question": "Show all customers from USA",
        "sql": "SELECT * FROM customers WHERE country = 'USA';"
    },
    {
        "question": "What is the total revenue from completed orders?",
        "sql": "SELECT SUM(total_amount) AS total_revenue FROM orders WHERE status = 'Completed';"
    },
    {
        "question": "List all products in Electronics category sorted by price descending",
        "sql": "SELECT product_name, price FROM products WHERE category = 'Electronics' ORDER BY price DESC;"
    },
    {
        "question": "How many orders has each customer placed?",
        "sql": "SELECT c.name, COUNT(o.order_id) AS order_count FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id GROUP BY c.customer_id, c.name;"
    }
]

class SchemaRetriever:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_schema_summary(self) -> str:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [row[0] for row in cursor.fetchall()]
        
        schema_lines = []
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table});")
            columns = cursor.fetchall()
            col_desc = ", ".join([f"{col[1]} ({col[2]})" for col in columns])
            schema_lines.append(f"Table '{table}': {col_desc}")
            
        conn.close()
        return "\n".join(schema_lines)

    def retrieve_relevant_examples(self, question: str, top_k: int = 2) -> List[Dict[str, str]]:
        q_words = set(question.lower().split())
        scored_examples = []
        for ex in SAMPLE_FEW_SHOT_EXAMPLES:
            ex_words = set(ex["question"].lower().split())
            overlap = len(q_words.intersection(ex_words))
            scored_examples.append((overlap, ex))
        
        scored_examples.sort(key=lambda x: x[0], reverse=True)
        return [ex for _, ex in scored_examples[:top_k]]
