"""Main entry point for Policy Compliance Agent."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from compliance_engine import PolicyComplianceEngine

def main():
    print("=" * 60)
    print("      POLICY COMPLIANCE AGENT - PROJECT 06")
    print("=" * 60)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    policies_file = os.path.join(base_dir, "data", "policies.json")

    engine = PolicyComplianceEngine(policies_file)

    sample_claims = [
        {"claim_id": "CLM-001", "amount": 120.50, "category": "Travel", "merchant": "Delta Airlines", "has_receipt": True},
        {"claim_id": "CLM-002", "amount": 1500.00, "category": "Software", "merchant": "AWS Cloud", "has_receipt": True},
        {"claim_id": "CLM-003", "amount": 75.00, "category": "Meals", "merchant": "Casino", "has_receipt": False},
        {"claim_id": "CLM-004", "amount": 85.00, "category": "Office Supplies", "merchant": "Staples", "has_receipt": False}
    ]

    for idx, claim in enumerate(sample_claims, 1):
        print(f"\n[{idx}] Evaluating Claim: {claim['claim_id']} (${claim['amount']} - {claim['category']})")
        res = engine.evaluate_expense_claim(claim)
        print(f"    Compliance Status: {res['status']}")
        if res['violations']:
            print(f"    Violations ({len(res['violations'])}):")
            for v in res['violations']:
                print(f"      - {v}")
        if res['warnings']:
            print(f"    Warnings ({len(res['warnings'])}):")
            for w in res['warnings']:
                print(f"      - {w}")
        print(f"    Human Review Flagged: {res['requires_human_review']}")
        print("-" * 60)

    print("\n[OK] Project 06 Policy Compliance Agent execution finished successfully.")

if __name__ == "__main__":
    main()
