import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from search.rerank import search_with_rerank

def search_manual(question):
    """Retrieves the best matching manual/troubleshooting chunks for a question."""
    results = search_with_rerank(question, final_k=3, candidate_pool=25)
    return {
        "tool": "search_manual",
        "chunks": results
    }

def check_schedule(question):
    """Looks up maintenance schedule/interval info."""
    results = search_with_rerank(question, final_k=3, candidate_pool=25)
    return {
        "tool": "check_schedule",
        "chunks": results
    }

def log_issue(question):
    """Records a newly reported problem. Minimal version: logs to console.
    Could be extended to write into a dedicated issues table in Supabase."""
    print(f"[ISSUE LOGGED] {question}")
    return {
        "tool": "log_issue",
        "message": "Your issue has been logged for the maintenance team to review.",
        "logged_text": question
    }

def escalate(question):
    """Returns a clear hand-off message instead of attempting an uncertain answer."""
    return {
        "tool": "escalate",
        "message": "This question needs review by a qualified technician. Please contact your maintenance supervisor."
    }

TOOL_MAP = {
    "search_manual": search_manual,
    "check_schedule": check_schedule,
    "log_issue": log_issue,
    "escalate": escalate
}

if __name__ == "__main__":
    test_cases = [
        ("search_manual", "What causes E-322 and how do I fix it?"),
        ("check_schedule", "When should I replace the coolant filter?"),
        ("log_issue", "The spindle just made a loud grinding noise and stopped"),
        ("escalate", "asdkjaskjd random gibberish")
    ]
    for tool_name, question in test_cases:
        print(f"=== Tool: {tool_name} ===")
        result = TOOL_MAP[tool_name](question)
        print(result)
        print()