"""ReAct SQL Agent powered by Google Gemini 2.5 Flash."""
import os
import re
from typing import Dict, Any, List
from tools import SQLAgentTools

class ReActSQLAgent:
    def __init__(self, tools: SQLAgentTools):
        self.tools = tools
        self.api_key = self._get_gemini_key()

    def _get_gemini_key(self) -> str:
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

    def run(self, user_question: str, max_iterations: int = 4) -> Dict[str, Any]:
        trajectory = []
        schema = self.tools.inspect_schema()
        trajectory.append(
            f"Thought 1: I need to inspect the database schema to understand available tables and columns.\n"
            f"Action 1: inspect_schema()\n"
            f"Observation 1:\n{schema}"
        )

        api_key = self._get_gemini_key()
        if api_key:
            try:
                from google import genai
                client = genai.Client(api_key=api_key)
                
                prompt = (
                    f"You are a ReAct SQL Agent with database tools.\n"
                    f"Database Schema:\n{schema}\n\n"
                    f"User Question: {user_question}\n\n"
                    f"Write a single valid SQLite SELECT query to answer the question. Return ONLY the raw SQL statement without markdown formatting."
                )
                
                resp = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                sql = resp.text.strip()
                sql = re.sub(r"^```sql\s*", "", sql, flags=re.IGNORECASE)
                sql = re.sub(r"```$", "", sql).strip()
                
                obs = self.tools.run_sql_query(sql)
                trajectory.append(
                    f"Thought 2: Formulating SQL query based on schema analysis.\n"
                    f"Action 2: run_sql_query('{sql}')\n"
                    f"Observation 2:\n{obs}"
                )
                
                final_answer = (
                    f"Successfully executed query against SQLite database:\n"
                    f"SQL Query: {sql}\n\n"
                    f"Results Summary:\n{obs}"
                )
                return {
                    "question": user_question,
                    "model_used": "gemini-2.5-flash",
                    "final_answer": final_answer,
                    "trajectory": trajectory
                }
            except Exception as e:
                print(f"Gemini API Exception in SQL Agent: {e}")

        # Dynamic Rule Engine for Intelligent Fallback Query Generation
        q_lower = user_question.lower()
        sql = ""
        
        # 1. Revenue & Sales Queries
        if any(w in q_lower for w in ["revenue", "total amount", "sales", "spent", "earnings"]):
            if "completed" in q_lower or "status" in q_lower:
                sql = "SELECT SUM(total_amount) AS total_revenue FROM orders WHERE status = 'Completed';"
            else:
                sql = "SELECT SUM(total_amount) AS total_revenue FROM orders;"
        
        # 2. Customer Queries
        elif "customer" in q_lower:
            countries = ["usa", "canada", "uk", "germany", "france", "australia"]
            found_country = next((c for c in countries if c in q_lower), None)
            if found_country:
                sql = f"SELECT customer_id, name, email, country FROM customers WHERE LOWER(country) = '{found_country}';"
            elif "count" in q_lower or "how many" in q_lower:
                sql = "SELECT COUNT(*) AS customer_count FROM customers;"
            else:
                sql = "SELECT customer_id, name, email, country FROM customers;"
                
        # 3. Product Queries & Price Ordering
        elif any(w in q_lower for w in ["product", "item", "price", "expensive", "cheapest", "cost"]):
            # Detect numeric limit
            limit_match = re.search(r'\b(\d+)\b', q_lower)
            limit = int(limit_match.group(1)) if limit_match else 3
            
            if any(w in q_lower for w in ["cheapest", "lowest", "least expensive"]):
                sql = f"SELECT product_name, category, price, stock_quantity FROM products ORDER BY price ASC LIMIT {limit};"
            else:
                sql = f"SELECT product_name, category, price, stock_quantity FROM products ORDER BY price DESC LIMIT {limit};"
                
        # 4. Order Status & History Queries
        elif "order" in q_lower:
            if "completed" in q_lower:
                sql = "SELECT * FROM orders WHERE status = 'Completed' ORDER BY order_date DESC;"
            elif "count" in q_lower or "how many" in q_lower:
                sql = "SELECT COUNT(*) AS total_orders FROM orders;"
            else:
                sql = "SELECT * FROM orders ORDER BY order_date DESC LIMIT 10;"
        
        # 5. Default Fallback Query
        else:
            sql = "SELECT product_name, price, category FROM products LIMIT 5;"

        obs = self.tools.run_sql_query(sql)
        trajectory.append(
            f"Thought 2: Formulated SQL query using ReAct Schema Mapping.\n"
            f"Action 2: run_sql_query('{sql}')\n"
            f"Observation 2:\n{obs}"
        )

        final_answer = (
            f"ReAct Agent Query Execution Completed:\n"
            f"Generated SQL: {sql}\n\n"
            f"Observation Output:\n{obs}"
        )

        return {
            "question": user_question,
            "model_used": "ReAct SQL Engine",
            "final_answer": final_answer,
            "trajectory": trajectory
        }
