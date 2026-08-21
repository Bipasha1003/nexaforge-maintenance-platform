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

ROUTER_PROMPT = """You are a query classifier for a manufacturing equipment maintenance assistant.
Classify the user's question into exactly ONE of these categories:

- search_manual: troubleshooting, error codes, procedures, how something works/is fixed — from the manuals
- check_schedule: generic maintenance interval questions ("how often should X be lubricated") — from the manuals
- machine_info: questions about which machines exist on the floor, a specific machine's CURRENT status, its next scheduled maintenance date, open issues, or last check-in — this is live fleet data, not from a manual
- log_issue: the user is reporting a new problem they just observed, not asking a question
- escalate: unclear, unsafe, or doesn't fit the other categories

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
        "asdkjaskjd random gibberish"
    ]
    for q in test_questions:
        category = classify_query(q)
        print(f"Q: {q}")
        print(f"-> {category}\n")