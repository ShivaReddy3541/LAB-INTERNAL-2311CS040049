"""FastAPI web server for Policy Compliance Agent powered by Google Gemini 2.5 Flash."""
import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from compliance_engine import PolicyComplianceEngine

app = FastAPI(title="Policy Compliance AI Studio", version="1.0.0")

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
policies_file = os.path.join(base_dir, "data", "policies.json")

engine = PolicyComplianceEngine(policies_file)

static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

class ClaimRequest(BaseModel):
    claim_id: str
    amount: float
    category: str
    merchant: str
    has_receipt: bool

@app.get("/", response_class=HTMLResponse)
def read_root():
    html_file = os.path.join(static_dir, "index.html")
    if os.path.exists(html_file):
        return FileResponse(html_file)
    return HTMLResponse("<h2>Policy Compliance Web App</h2>")

@app.post("/api/audit-claim")
def audit_claim(claim: ClaimRequest):
    res = engine.evaluate_expense_claim(claim.dict())
    return res

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8006)
