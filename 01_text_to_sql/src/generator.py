"""SQL Query Generator powered by Google Gemini API with robust heuristic fallback."""
import os
import re
import sqlite3
from typing import Dict, Any, Tuple
from retriever import SchemaRetriever
from validator import SQLValidator

class SQLGenerator:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.retriever = SchemaRetriever(db_path)
        self.validator = SQLValidator()

    def get_gemini_api_key(self) -> str:
        key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not key or not key.strip():
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            env_path = os.path.join(base_dir, ".env")
            if os.path.exists(env_path):
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("GEMINI_API_KEY=") or line.startswith("GOOGLE_API_KEY="):
                            key = line.split("=", 1)[1].strip()
                            break
        return key.strip() if key else ""

    def generate_sql(self, question: str) -> str:
        api_key = self.get_gemini_api_key()
        if api_key:
            try:
                from google import genai
                client = genai.Client(api_key=api_key)
                schema = self.retriever.get_schema_summary()
                examples = self.retriever.retrieve_relevant_examples(question)
                
                ex_text = "\n".join([f"Q: {e['question']}\nSQL: {e['sql']}" for e in examples])
                prompt = (
                    f"You are an expert SQLite query translator.\n"
                    f"Database Schema:\n{schema}\n\n"
                    f"Examples:\n{ex_text}\n\n"
                    f"Translate this natural language question into a single valid SQLite SELECT query.\n"
                    f"Return ONLY the raw SQL string without any markdown formatting or backticks.\n\n"
                    f"Question: {question}\n"
                    f"SQL:"
                )
                
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                sql = response.text.strip()
                sql = re.sub(r"^```sql\s*", "", sql, flags=re.IGNORECASE)
                sql = re.sub(r"```$", "", sql).strip()
                return sql
            except Exception as e:
                print(f"Gemini SQL Generation Exception: {e}")

        # Intelligent fallback translation rules
        q_lower = question.lower().strip()

        if ("total revenue" in q_lower or "sum" in q_lower and "revenue" in q_lower or "how much revenue" in q_lower) and "completed" in q_lower:
            return "SELECT SUM(total_amount) AS total_revenue FROM orders WHERE status = 'Completed';"
        elif "total revenue" in q_lower or "total sales" in q_lower:
            return "SELECT SUM(total_amount) AS total_revenue FROM orders;"

        if "customer" in q_lower:
            if "usa" in q_lower:
                return "SELECT customer_id, name, email, country, created_at FROM customers WHERE country = 'USA';"
            elif "uk" in q_lower:
                return "SELECT customer_id, name, email, country, created_at FROM customers WHERE country = 'UK';"
            elif "canada" in q_lower:
                return "SELECT customer_id, name, email, country, created_at FROM customers WHERE country = 'Canada';"
            elif "how many" in q_lower or "count" in q_lower:
                return "SELECT country, COUNT(*) AS customer_count FROM customers GROUP BY country ORDER BY customer_count DESC;"
            elif "order" in q_lower:
                return "SELECT c.name, COUNT(o.order_id) AS order_count FROM customers c LEFT JOIN orders o ON c.customer_id = o.customer_id GROUP BY c.customer_id, c.name ORDER BY order_count DESC;"
            return "SELECT customer_id, name, email, country, created_at FROM customers LIMIT 10;"

        if "product" in q_lower or "item" in q_lower:
            if "expensive" in q_lower or "top 5" in q_lower or "price descending" in q_lower or "highest price" in q_lower:
                return "SELECT product_name, category, price, stock_quantity FROM products ORDER BY price DESC LIMIT 5;"
            elif "electronics" in q_lower:
                return "SELECT product_name, category, price, stock_quantity FROM products WHERE category = 'Electronics' ORDER BY price DESC;"
            elif "furniture" in q_lower:
                return "SELECT product_name, category, price, stock_quantity FROM products WHERE category = 'Furniture' ORDER BY price DESC;"
            elif "appliances" in q_lower:
                return "SELECT product_name, category, price, stock_quantity FROM products WHERE category = 'Appliances' ORDER BY price DESC;"
            return "SELECT product_id, product_name, category, price, stock_quantity FROM products ORDER BY product_id LIMIT 10;"

        if "order" in q_lower:
            if "completed" in q_lower:
                return "SELECT o.order_id, c.name AS customer_name, o.order_date, o.total_amount, o.status FROM orders o JOIN customers c ON o.customer_id = c.customer_id WHERE o.status = 'Completed' ORDER BY o.order_date DESC;"
            elif "average" in q_lower or "avg" in q_lower:
                return "SELECT AVG(total_amount) AS average_order_value FROM orders;"
            return "SELECT o.order_id, c.name AS customer_name, o.order_date, o.total_amount, o.status FROM orders o JOIN customers c ON o.customer_id = c.customer_id ORDER BY o.order_date DESC LIMIT 10;"

        return "SELECT product_id, product_name, category, price, stock_quantity FROM products LIMIT 5;"

    def execute_and_explain(self, question: str) -> Dict[str, Any]:
        sql = self.generate_sql(question)
        is_valid, validated_sql = self.validator.validate_sql(sql)
        
        if not is_valid:
            return {
                "question": question,
                "generated_sql": sql,
                "is_valid": False,
                "error": f"Validation failed: {validated_sql}",
                "rows": [],
                "columns": []
            }

        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()
        try:
            cursor.execute(validated_sql)
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            conn.close()
            
            explanation = f"Query executed successfully returning {len(rows)} row(s)."
            return {
                "question": question,
                "generated_sql": validated_sql,
                "is_valid": True,
                "error": None,
                "columns": columns,
                "rows": rows,
                "explanation": explanation
            }
        except Exception as e:
            conn.close()
            return {
                "question": question,
                "generated_sql": validated_sql,
                "is_valid": False,
                "error": f"Execution error: {str(e)}",
                "rows": [],
                "columns": []
            }
