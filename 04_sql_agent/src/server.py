"""FastAPI web server for SQL Agent with Tool Use powered by Google Gemini 2.5 Flash."""
import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools import SQLAgentTools
from agent import ReActSQLAgent

app = FastAPI(title="SQL ReAct Agent AI Studio", version="1.0.0")

tools = SQLAgentTools()
agent = ReActSQLAgent(tools)

static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

class AgentQuery(BaseModel):
    question: str

@app.get("/", response_class=HTMLResponse)
def read_root():
    html_file = os.path.join(static_dir, "index.html")
    if os.path.exists(html_file):
        return FileResponse(html_file)
    return HTMLResponse("<h2>SQL ReAct Agent Web App</h2>")

@app.post("/api/run-agent")
def run_agent_query(req: AgentQuery):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    result = agent.run(req.question.strip())
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8004)
