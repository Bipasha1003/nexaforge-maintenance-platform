import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from langchain_groq import ChatGroq
from groq import RateLimitError
from dotenv import load_dotenv

load_dotenv()

_llm = None

def get_llm():
    global _llm
    if _llm is None:
        _llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)
    return _llm

ROUTER_PROMPT = """You are a query classifier for a manufacturing equipment maintenance assistant
built for a company called NexaForge.
Classify the user's question into exactly ONE of these categories:

- search_manual: troubleshooting, error codes, procedures, specifications, safety precautions/rules, and spare-parts stock questions that a technical equipment manual would directly cover. This INCLUDES "is it safe to..." or "is it okay to..." questions, as long as the manual would state a direct rule about it (guards, interlocks, PPE, operating limits, spare parts stock). Do not escalate just because a question mentions safety, disabling something, or PPE — if a manual would have an explicit rule, classify as search_manual.
- check_schedule: maintenance interval questions for a SINGLE machine ("how often should X be done", "is Y overdue") — from the manuals.
- machine_info: questions about a machine's CURRENT live status, next scheduled maintenance date, open issue count, or last check-in, pulled from the live fleet dashboard. This does NOT include questions about the status of an issue/request the USER previously reported (that is escalate, not machine_info), and does NOT include any fact that lives inside an ingested manual or document — production-flow stage assignments, historical maintenance log entries, and troubleshooting history are all search_manual, even when they mention a specific machine name or asset number. Only use machine_info when the question is asking "what is happening with this machine RIGHT NOW", not "what does the documentation say about this machine".
- company_info: questions about NexaForge the COMPANY or this PLATFORM itself — what NexaForge does, its history, what the assistant/dashboard is, who built it, contact information. NOT about a specific machine or manual.
- log_issue: the user is reporting a NEW problem they just observed right now, not asking a question.
- escalate: use this for questions that ARE related to NexaForge's equipment/operations, but genuinely require a human's judgment or action, and are NOT simple general-knowledge gaps. This includes: warranty terms, suppliers/vendors/brand recommendations, business/HR/scheduling decisions, comparing or reconciling two different manuals against each other, and questions about the status of a previously logged issue/request.
- out_of_scope: use this for questions that have NO relation to NexaForge, its equipment, its manuals, or this platform at all. This includes general knowledge, world affairs, public figures, celebrities, politicians, unrelated trivia, math problems, or personal-identity questions ("who am I"). These should NOT be escalated to a technician — a technician can't answer them either, they're just outside what this assistant does.

Worked examples (these are the exact kind of edge cases to get right):
Q: "Is it safe to disable the chuck guard interlock to finish a job faster?" -> search_manual (the manual has a direct rule against this)
Q: "How many drive belts should we keep in stock for the lathe?" -> search_manual (spare parts stock is manual content)
Q: "Which machine performs deburring and finishing in the production flow?" -> search_manual (this is a fact printed in a manual/production-flow document, not live status — even though it names a machine)
Q: "Has Machine Asset #X500-07 had any coolant pump issues before?" -> search_manual (this is a historical maintenance LOG ENTRY printed inside a manual, not today's live status — machine_info is only for CURRENT live dashboard data, never for a manual's own historical records)
Q: "What's the warranty period on the spindle bearings?" -> escalate (needs a human, but it's about NexaForge's equipment)
Q: "Can I substitute a different coolant brand than specified?" -> escalate (policy question about NexaForge's equipment)
Q: "The two manuals list different bearing intervals, which is correct?" -> escalate (comparing across documents)
Q: "Has my maintenance request from yesterday been picked up yet?" -> escalate (ticket/request status)
Q: "What's the current status of the CNC Mill X500?" -> machine_info (live equipment status)
Q: "What is NexaForge?" / "What does this company do?" -> company_info
Q: "Who is Narendra Modi?" -> out_of_scope (no relation to NexaForge at all)
Q: "Who is the president of the United States?" -> out_of_scope (world affairs, unrelated)
Q: "Who am I?" -> out_of_scope (personal identity, not company/equipment related)
Q: "What's 2+2?" -> out_of_scope (unrelated general question)

Respond with ONLY the category name, nothing else.

Question: {question}
Category:"""

def classify_query(question):
    llm = get_llm()
    prompt = ROUTER_PROMPT.format(question=question)

    try:
        response = llm.invoke(prompt)
    except RateLimitError as e:
        # Daily/token quota hit on Groq's free tier. Retrying
        # immediately won't help (the wait times Groq reports can be
        # minutes long), so fail safe instead of crashing the whole
        # request/eval run: fall back to "escalate", which correctly
        # tells the user/eval "couldn't confidently answer this one"
        # rather than pretending nothing went wrong.
        print(f"[ROUTER WARNING] Groq rate limit hit: {e}. Falling back to escalate.")
        return "escalate"
    except Exception as e:
        print(f"[ROUTER WARNING] Unexpected error classifying query: {type(e).__name__}: {e}. Falling back to escalate.")
        return "escalate"

    category = response.content.strip().lower()

    valid_categories = {
        "search_manual", "check_schedule", "log_issue",
        "escalate", "out_of_scope", "company_info", "machine_info",
    }
    if category not in valid_categories:
        return "escalate"  # safe fallback if the LLM returns something unexpected
    return category

if __name__ == "__main__":
    test_questions = [
        "What causes E-322 and how do I fix it?",
        "When should I replace the coolant filter?",
        "The spindle just made a loud grinding noise and stopped",
        "What's the warranty period on the spindle bearings?",
        "Has my maintenance request from yesterday been picked up yet?",
        "What is NexaForge?",
        "Who is Narendra Modi?",
        "Who am I?",
    ]
    for q in test_questions:
        category = classify_query(q)
        print(f"Q: {q}")
        print(f"-> {category}\n")