"""FastAPI web server for Text-to-SQL Workflow with Real-Time Live Data Streaming."""
import datetime
import os
import random
import sqlite3
import sys
import threading
import time
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sample_database import initialize_database, get_db_path
from generator import SQLGenerator
from retriever import SchemaRetriever

app = FastAPI(title="Text-to-SQL Real-Time AI Studio", version="2.0.0")

db_path = get_db_path()
initialize_database(db_path)
generator = SQLGenerator(db_path)
retriever = SchemaRetriever(db_path)

static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

def insert_realtime_order():
    conn = sqlite3.connect(db_path, timeout=30.0)
    cursor = conn.cursor()
    
    # Pick random customer and product
    cursor.execute("SELECT customer_id FROM customers ORDER BY RANDOM() LIMIT 1;")
    cust_row = cursor.fetchone()
    cust_id = cust_row[0] if cust_row else 1

    cursor.execute("SELECT product_id, price FROM products ORDER BY RANDOM() LIMIT 1;")
    prod_row = cursor.fetchone()
    if prod_row:
        prod_id, price = prod_row
    else:
        prod_id, price = 1, 1299.99

    qty = random.randint(1, 3)
    total_amount = round(qty * price, 2)
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        "INSERT INTO orders (customer_id, order_date, total_amount, status) VALUES (?, ?, ?, 'Completed');",
        (cust_id, now_str, total_amount)
    )
    order_id = cursor.lastrowid

    cursor.execute(
        "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?);",
        (order_id, prod_id, qty, price)
    )

    conn.commit()
    conn.close()
    return order_id, now_str, total_amount

# Background thread for continuous real-time data stream (1 transaction every 6 seconds)
def background_realtime_stream():
    while True:
        try:
            insert_realtime_order()
        except Exception:
            pass
        time.sleep(6)

stream_thread = threading.Thread(target=background_realtime_stream, daemon=True)
stream_thread.start()

class QueryRequest(BaseModel):
    question: str

@app.get("/", response_class=HTMLResponse)
def read_root():
    html_file = os.path.join(static_dir, "index.html")
    if os.path.exists(html_file):
        return FileResponse(html_file)
    return HTMLResponse("<h2>Text-to-SQL Real-Time Web Application</h2>")

@app.get("/api/schema")
def get_schema():
    schema_summary = retriever.get_schema_summary()
    return {"schema": schema_summary}

@app.get("/api/realtime-stats")
def get_realtime_stats():
    conn = sqlite3.connect(db_path, timeout=30.0)
    cursor = conn.cursor()
    
    cursor.execute("SELECT SUM(total_amount) FROM orders WHERE status = 'Completed';")
    rev = cursor.fetchone()[0] or 0.0

    cursor.execute("SELECT COUNT(*) FROM orders;")
    total_orders = cursor.fetchone()[0] or 0

    cursor.execute("SELECT order_id, order_date, total_amount FROM orders ORDER BY order_id DESC LIMIT 1;")
    latest = cursor.fetchone()
    
    conn.close()
    
    return {
        "live_revenue": round(rev, 2),
        "total_orders": total_orders,
        "latest_order": {
            "order_id": latest[0] if latest else None,
            "timestamp": latest[1] if latest else None,
            "amount": latest[2] if latest else 0.0
        } if latest else None
    }

@app.post("/api/simulate-live-order")
def simulate_live_order():
    order_id, now_str, amount = insert_realtime_order()
    return {
        "message": "Real-time live transaction created successfully.",
        "order_id": order_id,
        "timestamp": now_str,
        "amount": amount
    }

@app.post("/api/query")
def execute_query(req: QueryRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    result = generator.execute_and_explain(req.question.strip())
    return result

from fastapi.responses import StreamingResponse

@app.get("/api/stream-explain")
def stream_sql_explanation(sql: str = "", question: str = ""):
    def event_generator():
        text = f"Analyzing generated SQL statement '{sql}' for natural question '{question}':\n"
        text += "- Reads schema structure and filters matching records using standard SQL predicates.\n"
        text += "- Validates query for security and executes safely against the SQLite database instance.\n"
        text += "- Returns tabular results with automatic chart visualization."
        for word in text.split(" "):
            yield f"data: {word} \n\n"
            time.sleep(0.04)
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
