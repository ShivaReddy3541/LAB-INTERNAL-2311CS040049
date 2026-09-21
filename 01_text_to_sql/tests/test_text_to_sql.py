import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from sample_database import initialize_database
from validator import SQLValidator
from generator import SQLGenerator

@pytest.fixture
def db_path(tmp_path):
    path = str(tmp_path / "test.db")
    initialize_database(path)
    return path

def test_database_initialization(db_path):
    assert os.path.exists(db_path)

def test_sql_validator_valid():
    validator = SQLValidator()
    is_valid, cleaned = validator.validate_sql("SELECT * FROM customers WHERE country = 'USA';")
    assert is_valid is True
    assert cleaned == "SELECT * FROM customers WHERE country = 'USA'"

def test_sql_validator_forbidden():
    validator = SQLValidator()
    is_valid, msg = validator.validate_sql("DROP TABLE customers;")
    assert is_valid is False
    assert "Forbidden" in msg or "Only SELECT" in msg

def test_generator_execution(db_path):
    generator = SQLGenerator(db_path)
    result = generator.execute_and_explain("Show all customers located in USA")
    assert result["is_valid"] is True
    assert len(result["rows"]) > 0
    assert "customer_id" in result["columns"] or "name" in result["columns"]
