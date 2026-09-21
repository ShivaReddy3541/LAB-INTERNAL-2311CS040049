import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from tools import SQLAgentTools
from agent import ReActSQLAgent

@pytest.fixture
def agent_tools(tmp_path):
    db_file = str(tmp_path / "test_agent.db")
    return SQLAgentTools(db_file)

def test_tools_schema_inspection(agent_tools):
    schema = agent_tools.inspect_schema()
    assert "customers" in schema
    assert "products" in schema

def test_tools_sql_validation(agent_tools):
    assert agent_tools.validate_sql("SELECT * FROM products") == "VALID"
    assert agent_tools.validate_sql("SELECT customer_id, created_at FROM customers") == "VALID"
    assert "ERROR" in agent_tools.validate_sql("DELETE FROM products")
    assert "ERROR" in agent_tools.validate_sql("DROP TABLE customers")

def test_react_agent_run(agent_tools):
    agent = ReActSQLAgent(agent_tools)
    res = agent.run("Show top 3 products")
    assert len(res["trajectory"]) >= 2
    assert "Final Answer" in res["final_answer"] or "Columns" in res["final_answer"]
