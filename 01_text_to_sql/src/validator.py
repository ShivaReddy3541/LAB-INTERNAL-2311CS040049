"""SQL safety validator for Text-to-SQL Workflow."""
import re
from typing import Tuple

FORBIDDEN_KEYWORDS = [
    "DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", "TRUNCATE",
    "REPLACE", "GRANT", "REVOKE", "EXEC", "EXECUTE", "ATTACH", "DETACH"
]

class SQLValidator:
    @staticmethod
    def validate_sql(sql_query: str) -> Tuple[bool, str]:
        cleaned_sql = sql_query.strip()
        if not cleaned_sql:
            return False, "Query is empty."
        
        # Strip trailing semicolon if present
        if cleaned_sql.endswith(";"):
            cleaned_sql = cleaned_sql[:-1].strip()

        # Check for multiple statements
        if ";" in cleaned_sql:
            return False, "Multiple SQL statements detected; only single SELECT queries are permitted."

        upper_sql = cleaned_sql.upper()
        if not upper_sql.startswith("SELECT") and not upper_sql.startswith("WITH"):
            return False, "Only SELECT queries are allowed."

        for keyword in FORBIDDEN_KEYWORDS:
            pattern = r'\b' + keyword + r'\b'
            if re.search(pattern, upper_sql):
                return False, f"Forbidden SQL keyword '{keyword}' detected. Only read-only operations permitted."

        return True, cleaned_sql
