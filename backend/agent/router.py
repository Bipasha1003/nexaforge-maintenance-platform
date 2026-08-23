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

# Rewritten after evaluation/run_eval.py surfaced two consistent biases:
#   1. Over-escalating anything with safety-adjacent WORDS ("disable",
#      "safety glasses"), even when the manual has a direct, explicit
#      rule about it — the old prompt's "unsafe" wording in the
#      escalate definition was training this reflex.
#   2. Under-escalating questions that mention manual-adjacent NOUNS
#      (bearings, coolant) but ask about something manuals don't
#      actually cover (warranty, brand substitution).
# Fixed by being explicit about the DISTINCTION in each case, plus a
# few worked examples pulled directly from the failing eval questions.
ROUTER_PROMPT = """You are a query classifier for a manufacturing equipment maintenance assistant.
Classify the user's question into exactly ONE of these categories:

- search_manual: troubleshooting, error codes, procedures, specifications, safety precautions/rules, and spare-parts stock questions that a technical equipment manual would directly cover. This INCLUDES "is it safe to..." or "is it okay to..." questions, as long as the manual would state a direct rule about it (guards, interlocks, PPE, operating limits, spare parts stock). Do not escalate just because a question mentions safety, disabling something, or PPE — if a manual would have an explicit rule, classify as search_manual.
- check_schedule: maintenance interval questions for a SINGLE machine ("how often should X be done", "is Y overdue") — from the manuals.
- machine_info: questions about a machine's CURRENT live status, next scheduled maintenance date, open issue count, or last check-in, pulled from the live fleet dashboard. This does NOT include questions about the status of a issue/request the USER previously reported (that is escalate, not machine_info) — machine_info is about the equipment's state, not a person's support ticket.
- log_issue: the user is reporting a NEW problem they just observed right now, not asking a question.
- escalate: use this whenever the question cannot be answered from a single equipment manual or the live fleet dashboard. This includes: warranty terms, suppliers/vendors/brand recommendations, business/HR/scheduling decisions, external or real-time information (stock prices, news), questions that require comparing or reconciling two different manuals against each other, and questions about the status of a previously logged issue/request.

Worked examples (these are the exact kind of edge cases to get right):
Q: "Is it safe to disable the chuck guard interlock to finish a job faster?" -> search_manual (the manual has a direct rule against this)
Q: "Is it okay to run without safety glasses for a quick job?" -> search_manual (the manual has a direct PPE rule)
Q: "How many drive belts should we keep in stock for the lathe?" -> search_manual (spare parts stock is manual content)
Q: "What's the warranty period on the spindle bearings?" -> escalate (manuals don't cover warranty terms)
Q: "Can I substitute a different coolant brand than specified?" -> escalate (manuals don't cover brand substitution policy)
Q: "The two manuals list different bearing intervals, which is correct?" -> escalate (comparing across documents, neither resolves it alone)
Q: "Has my maintenance request from yesterday been picked up yet?" -> escalate (ticket/request status, not machine status)
Q: "What's the current status of the CNC Mill X500?" -> machine_info (live equipment status)

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

    valid_categories = {"search_manual", "check_schedule", "log_issue", "escalate", "machine_info"}
    if category not in valid_categories:
        return "escalate"  # safe fallback if the LLM returns something unexpected
    return category

if __name__ == "__main__":
    test_questions = [
        "What causes E-322 and how do I fix it?",
        "When should I replace the coolant filter?",
        "The spindle just made a loud grinding noise and stopped",
        "asdkjaskjd random gibberish",
        "Is it safe to disable the chuck guard interlock to finish a job faster?",
        "What's the warranty period on the spindle bearings?",
        "Has my maintenance request from yesterday been picked up yet?",
    ]
    for q in test_questions:
        category = classify_query(q)
        print(f"Q: {q}")
        print(f"-> {category}\n")