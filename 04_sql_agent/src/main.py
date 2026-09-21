"""Main entry point for SQL Agent with Tool Use."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools import SQLAgentTools
from agent import ReActSQLAgent

def main():
    print("=" * 60)
    print("    SQL AGENT WITH TOOL USE (REACT) - PROJECT 04")
    print("=" * 60)

    tools = SQLAgentTools()
    agent = ReActSQLAgent(tools)

    sample_questions = [
        "What are the top 3 most expensive products?",
        "How much total revenue came from completed orders?",
        "Show all customers from the USA"
    ]

    for idx, q in enumerate(sample_questions, 1):
        print(f"\n[{idx}] Question: '{q}'")
        res = agent.run(q)
        print("  Trajectory:")
        for step in res["trajectory"]:
            print(f"    {step}")
        print(f"\n  Final Answer: {res['final_answer']}")
        print("-" * 60)

    print("\n[OK] Project 04 SQL Agent execution finished successfully.")

if __name__ == "__main__":
    main()
