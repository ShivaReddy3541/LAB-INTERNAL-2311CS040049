"""Main entry point for Text-to-SQL Workflow."""
import os
import sys

# Ensure src module directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sample_database import initialize_database, get_db_path
from generator import SQLGenerator

def main():
    print("=" * 60)
    print("      TEXT-TO-SQL WORKFLOW - PROJECT 01 EXECUTION")
    print("=" * 60)

    db_path = get_db_path()
    print(f"[*] Initializing sample e-commerce database at:\n    {db_path}")
    initialize_database(db_path)

    generator = SQLGenerator(db_path)
    
    sample_questions = [
        "Show all customers located in USA",
        "List top 5 products sorted by price descending",
        "What is the total revenue from completed orders?",
        "Show all completed customer orders"
    ]

    print("\n--- Running Sample Queries ---\n")
    for idx, q in enumerate(sample_questions, 1):
        print(f"[{idx}] Question: '{q}'")
        res = generator.execute_and_explain(q)
        print(f"    Generated SQL: {res['generated_sql']}")
        print(f"    Valid: {res['is_valid']}")
        if res['is_valid']:
            print(f"    Columns: {res['columns']}")
            print(f"    Result Rows ({len(res['rows'])}):")
            for row in res['rows'][:3]:
                print(f"      - {row}")
            if len(res['rows']) > 3:
                print(f"      ... (+{len(res['rows']) - 3} more)")
        else:
            print(f"    Error: {res['error']}")
        print("-" * 60)

    print("\n[OK] Project 01 Text-to-SQL execution finished successfully.")

if __name__ == "__main__":
    main()
