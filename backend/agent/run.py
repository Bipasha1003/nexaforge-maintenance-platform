import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent.router import classify_query
from agent.actions import TOOL_MAP
from agent.state import get_history, add_exchange
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

def generate_answer(question, tool_result, history):
    history_text = "\n".join(f"Q: {h['question']}\nA: {h['answer']}" for h in history[-3:])

    if tool_result["tool"] in ("search_manual", "check_schedule"):
        context = "\n\n".join(
            f"[Page {c['page_number']}]\n{c['text']}" for c in tool_result["chunks"]
        )
        prompt = f"""Previous conversation:
{history_text}

Manual context:
{context}

Question: {question}

Answer strictly using only the context above. Cite the page number. 
If the question asks about something outside this manual context, unrelated topics, general knowledge, or world affairs, you must state politely that you do not have that information in the manuals."""
        llm = get_llm()

        try:
            response = llm.invoke(prompt)
        except RateLimitError as e:
            # Same Groq daily quota issue as router.py. Fail safe with
            # a clear message instead of crashing the request/eval —
            # the user (or eval script) gets an honest "try again
            # shortly" instead of a stack trace.
            print(f"[ANSWER WARNING] Groq rate limit hit: {e}. Returning fallback message.")
            return (
                "The AI service is temporarily at its usage limit — please try again in a few minutes.",
                [],
            )
        except Exception as e:
            print(f"[ANSWER WARNING] Unexpected error generating answer: {type(e).__name__}: {e}.")
            return (
                "Something went wrong generating an answer. Please try again.",
                [],
            )

        seen = set()
        sources = []
        for c in tool_result["chunks"]:
            key = (c["page_number"], c["source"])
            if key not in seen:
                seen.add(key)
                sources.append({"page": c["page_number"], "source": c["source"]})

        return response.content, sources

    elif tool_result["tool"] == "log_issue":
        return tool_result["message"], []

    else:  # escalate (handles out-of-bounds/general-knowledge queries cleanly)
        # Use the actual message actions.py's escalate() function
        # returns, instead of a different hardcoded string. Previously
        # this branch ignored tool_result["message"] entirely and
        # always said "I don't have that information in the manuals"
        # even for genuinely out-of-scope questions (stock prices,
        # overtime approval) where "ask a technician" is a more
        # honest and useful response than implying the manual was
        # searched and came up empty.
        return tool_result.get("message", "This question needs review by a qualified technician."), []

def run_agent(question, session_id="default"):
    history = get_history(session_id)
    
    # --- SMARTER QUERY CONTEXTUALIZATION FIX ---
    search_query = question
    if history:
        last_question = history[-1]['question']
        # Add spaces to prevent false positive matches inside other words
        follow_up_keywords = [" it ", " that ", " this ", " how ", " what about ", " why ", " explain "]
        
        # Pad the question with spaces so first/last words match correctly
        padded_q = f" {question.lower()} "
        is_short_or_followup = len(question.split()) <= 6 or any(kw in padded_q for kw in follow_up_keywords)
        
        if is_short_or_followup:
            search_query = f"{last_question} - {question}"
    # ---------------------------------------------

    category = classify_query(search_query)
    tool_result = TOOL_MAP[category](search_query)
    
    answer, sources = generate_answer(question, tool_result, history)
    add_exchange(session_id, question, answer)
    
    return {
        "answer": answer, 
        "sources": sources, 
        "tool_used": category
    }

def print_chat_reply(question, result):
    print(f"\nYou: {question}")
    print(f"Bot: {result['answer']}")
    if result["sources"]:
        pages = ", ".join(f"p.{s['page']}" for s in result["sources"])
        print(f"    (Source: {result['sources'][0]['source']} - {pages})")

if __name__ == "__main__":
    q1 = "What causes E-322 and how do I fix it?"
    r1 = run_agent(q1, session_id="test")
    print_chat_reply(q1, r1)