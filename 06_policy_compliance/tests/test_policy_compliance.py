import json
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from compliance_engine import PolicyComplianceEngine

@pytest.fixture
def policy_file(tmp_path):
    p = tmp_path / "test_pol.json"
    p.write_text(json.dumps({
        "expense_policy": {
            "max_single_transaction": 500.0,
            "receipt_required_above": 50.0,
            "allowed_categories": ["Travel"],
            "restricted_merchants": ["Casino"]
        }
    }), encoding="utf-8")
    return str(p)

def test_compliant_claim(policy_file):
    engine = PolicyComplianceEngine(policy_file)
    res = engine.evaluate_expense_claim({
        "claim_id": "1", "amount": 40.0, "category": "Travel", "merchant": "Uber", "has_receipt": True
    })
    assert res["status"] == "COMPLIANT"

def test_violating_claim(policy_file):
    engine = PolicyComplianceEngine(policy_file)
    res = engine.evaluate_expense_claim({
        "claim_id": "2", "amount": 600.0, "category": "Food", "merchant": "Casino", "has_receipt": False
    })
    assert res["status"] == "NON_COMPLIANT"
    assert len(res["violations"]) >= 2
    assert res["requires_human_review"] is True
