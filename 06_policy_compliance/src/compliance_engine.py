"""Policy Compliance Engine powered by Google Gemini 2.5 Flash."""
import json
import os
from typing import Dict, Any, List

class PolicyComplianceEngine:
    def __init__(self, policy_filepath: str):
        with open(policy_filepath, "r", encoding="utf-8") as f:
            self.policies = json.load(f)

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

    def evaluate_expense_claim(self, claim: Dict[str, Any]) -> Dict[str, Any]:
        exp = self.policies.get("expense_policy", {})
        violations = []
        warnings = []
        
        amount = claim.get("amount", 0.0)
        category = claim.get("category", "")
        merchant = claim.get("merchant", "")
        has_receipt = claim.get("has_receipt", False)

        if amount > exp.get("max_single_transaction", 1000.0):
            violations.append(f"Transaction amount ${amount:.2f} exceeds limit of ${exp['max_single_transaction']:.2f}")

        if category not in exp.get("allowed_categories", []):
            violations.append(f"Category '{category}' is not in allowed categories: {exp['allowed_categories']}")

        if merchant in exp.get("restricted_merchants", []):
            violations.append(f"Merchant '{merchant}' is explicitly restricted under policy guidelines.")

        if amount > exp.get("receipt_required_above", 50.0) and not has_receipt:
            warnings.append(f"Receipt required for expenses over ${exp['receipt_required_above']:.2f}.")

        status = "NON_COMPLIANT" if violations else ("WARNING" if warnings else "COMPLIANT")
        requires_human_review = status in ["WARNING", "NON_COMPLIANT"]

        # Generate reasoning via Gemini 2.5 Flash
        api_key = self._get_gemini_key()
        gemini_explanation = ""
        if api_key:
            try:
                from google import genai
                client = genai.Client(api_key=api_key)
                prompt = (
                    f"You are a Corporate Policy Compliance Auditor.\n"
                    f"Expense Claim: {claim}\n"
                    f"Compliance Status: {status}\n"
                    f"Violations Found: {violations}\n"
                    f"Warnings Found: {warnings}\n\n"
                    f"Write a 2-sentence formal compliance summary explaining the audit determination."
                )
                resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                gemini_explanation = resp.text.strip()
            except Exception as e:
                print(f"Gemini API Exception in Policy Compliance: {e}")

        if not gemini_explanation:
            summary_parts = []
            if status == "COMPLIANT":
                summary_parts.append(f"Claim {claim.get('claim_id')} of ${amount:.2f} for '{category}' at '{merchant}' fully complies with all corporate expense policy guidelines.")
            elif status == "NON_COMPLIANT":
                summary_parts.append(f"Claim {claim.get('claim_id')} (${amount:.2f} - {category}) at '{merchant}' was flagged as NON-COMPLIANT. Reason(s): {'; '.join(violations)}.")
            else:
                summary_parts.append(f"Claim {claim.get('claim_id')} (${amount:.2f}) passed core policy rules but raised policy warnings: {'; '.join(warnings)}.")
            gemini_explanation = " ".join(summary_parts)

        return {
            "claim_id": claim.get("claim_id"),
            "model_used": "gemini-2.5-flash",
            "status": status,
            "violations": violations,
            "warnings": warnings,
            "requires_human_review": requires_human_review,
            "explanation": gemini_explanation
        }
