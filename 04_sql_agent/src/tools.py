"""Tool definitions for ReAct SQL Agent."""
import os
import re
import sqlite3
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "01_text_to_sql", "src"))
from sample_database import initialize_database

class SQLAgentTools:
    def __init__(self, db_path: str = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, "data", "agent_db.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        initialize_database(db_path)
        self.db_path = db_path

    def inspect_schema(self) -> str:
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [r[0] for r in cursor.fetchall()]
        
        info = []
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table});")
            cols = cursor.fetchall()
            col_str = ", ".join([f"{c[1]} ({c[2]})" for c in cols])
            info.append(f"Table '{table}': {col_str}")
        conn.close()
        return "\n".join(info)

    def validate_sql(self, sql_query: str) -> str:
        sql = sql_query.strip().upper()
        if not sql.startswith("SELECT") and not sql.startswith("WITH"):
            return "ERROR: Only SELECT queries are permitted for safety."
        forbidden = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", "TRUNCATE"]
        for f in forbidden:
            if re.search(r'\b' + f + r'\b', sql):
                return f"ERROR: Forbidden keyword '{f}' found."
        return "VALID"

    def run_sql_query(self, sql_query: str) -> str:
        val = self.validate_sql(sql_query)
        if val != "VALID":
            return val

        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()
        try:
            cursor.execute(sql_query)
            cols = [d[0] for d in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            conn.close()
            return f"Columns: {cols}\nRows ({len(rows)}): {rows[:5]}"
        except Exception as e:
            conn.close()
            return f"SQL EXECUTION ERROR: {str(e)}"
