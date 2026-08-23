import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from search.rerank import search_with_rerank
from storage import machine_store

def search_manual(question):
    """Retrieves the best matching manual/troubleshooting chunks for a question."""
    results = search_with_rerank(question, final_k=5, candidate_pool=25)
    return {
        "tool": "search_manual",
        "chunks": results
    }

def check_schedule(question):
    """Looks up maintenance schedule/interval info."""
    results = search_with_rerank(question, final_k=5, candidate_pool=25)
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
    """For maintenance-ADJACENT questions the manuals/dashboard genuinely
    can't resolve, but that a real person still needs to act on — ticket
    status, warranty, business/HR decisions, brand-substitution policy,
    comparing conflicting manuals, safety judgment calls not covered by
    any manual. This is distinct from out_of_scope() below."""
    return {
        "tool": "escalate",
        "message": "This question needs review by a qualified technician. Please contact your maintenance supervisor."
    }

def out_of_scope(question):
    """For questions with NO relation to NexaForge, its equipment, or
    its manuals at all — general knowledge, world affairs, public
    figures, unrelated trivia, or personal-identity questions. These
    don't need a technician; they just aren't something this assistant
    was built to answer, so the response should say so plainly instead
    of implying a human needs to step in."""
    return {
        "tool": "out_of_scope",
        "message": "I don't have that information in the manuals. The provided sources do not contain details regarding your request."
    }

# Static facts about NexaForge itself — hardcoded rather than LLM-
# generated, since this is the one place where making something up
# would be worse than sounding slightly canned. Keep this in sync with
# frontend/src/pages/About.jsx and LandingPage.jsx if those change.
COMPANY_INFO = """NexaForge is a precision components and contract manufacturer, operating since 1998, specializing in high-tolerance components (±0.005mm precision), custom fabrication, and reliable industrial solutions for automotive and heavy-industrial clients.

NexaForge also runs a Fleet Console and Operations Dashboard that digitizes technical equipment manuals into a searchable knowledge base, powered by a hybrid Retrieval-Augmented Generation (RAG) pipeline. This AI assistant is part of that system — it helps factory floor workers and maintenance teams get instant, cited answers from ingested manuals, live equipment status, and maintenance schedules.

Contact: 123 Industrial Parkway | (555) 019-2834 | operations@nexaforge.com"""

def company_info(question):
    """Returns static info about NexaForge the company/platform itself
    — not a specific machine. Handles questions like 'what is
    NexaForge', 'what does this company do', 'who is this platform
    for', etc."""
    return {
        "tool": "company_info",
        "message": COMPANY_INFO,
    }

def machine_info(question):
    """Retrieves LIVE equipment fleet data (status, next maintenance,
    open issues) from the machines table — not from ingested manuals.
    Always reflects whatever the admin dashboard currently shows,
    since list_machines() queries Postgres fresh every call."""
    machines = machine_store.list_machines()
    return {
        "tool": "machine_info",
        "machines": machines,
    }

TOOL_MAP = {
    "search_manual": search_manual,
    "check_schedule": check_schedule,
    "log_issue": log_issue,
    "escalate": escalate,
    "out_of_scope": out_of_scope,
    "company_info": company_info,
    "machine_info": machine_info,
}

if __name__ == "__main__":
    test_cases = [
        ("search_manual", "What causes E-322 and how do I fix it?"),
        ("check_schedule", "When should I replace the coolant filter?"),
        ("log_issue", "The spindle just made a loud grinding noise and stopped"),
        ("escalate", "Has my maintenance request from yesterday been picked up yet?"),
        ("out_of_scope", "Who is Narendra Modi?"),
        ("company_info", "What is NexaForge?"),
    ]
    for tool_name, question in test_cases:
        print(f"=== Tool: {tool_name} ===")
        result = TOOL_MAP[tool_name](question)
        print(result)
        print()