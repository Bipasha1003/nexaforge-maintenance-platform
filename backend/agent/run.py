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

    elif tool_result["tool"] == "machine_info":
        machines = tool_result["machines"]

        if not machines:
            return "There are no machines currently registered in the fleet.", []

        fleet_context = "\n".join(
            f"- {m['name']} ({m['type']}): status={m['status']}, "
            f"next maintenance='{m['next_maintenance']}' ({m['next_maintenance_due']}), "
            f"open issues={m.get('open_issues', 0)}, last check-in={m.get('last_check_in', '—')}"
            for m in machines
        )

        prompt = f"""Current equipment fleet (live data, not from a manual):
{fleet_context}

Question: {question}

Answer using ONLY the fleet data above. Be specific — name exact machines, statuses, and due dates.
If asked to list machines, list all of them.
If asked about a specific machine and it is NOT in the list above, respond with exactly this
format: "<machine name> is not currently registered in the fleet." Do not say anything about
needing technician review, escalation, or contacting a supervisor — that phrasing is reserved
for a different feature and must never appear in your answer here."""
        llm = get_llm()

        try:
            response = llm.invoke(prompt)
        except RateLimitError as e:
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

        return response.content, []

    elif tool_result["tool"] == "log_issue":
        return tool_result["message"], []

    elif tool_result["tool"] == "company_info":
        return tool_result["message"], []

    elif tool_result["tool"] == "out_of_scope":
        return tool_result["message"], []

    else:  # escalate — genuinely needs a technician/human's judgment
        return tool_result.get("message", "This question needs review by a qualified technician."), []

def run_agent(question, session_id="default"):
    history = get_history(session_id)
    
    # --- SMARTER QUERY CONTEXTUALIZATION FIX ---
    search_query = question
    if history:
        last_question = history[-1]['question']
        follow_up_keywords = [" it ", " that ", " this ", " how ", " what about ", " why ", " explain "]
        padded_q = f" {question.lower()} "
        is_short_or_followup = len(question.split()) <= 6 or any(kw in padded_q for kw in follow_up_keywords)
        
        if is_short_or_followup:
            search_query = f"{last_question} - {question}"
    # ---------------------------------------------

    category = classify_query(search_query)

    # machine_info, company_info, escalate, and out_of_scope all
    # ignore search_query's rewritten form and just need the original
    # question — only manual retrieval benefits from the follow-up
    # rewrite. log_issue additionally needs to know WHO is reporting,
    # so its logged entry can actually be attributed on the
    # Maintenance Log instead of being anonymous — session_id is the
    # user's display name, set by api/query.py from req.user_id.
    if category in ("search_manual", "check_schedule"):
        tool_result = TOOL_MAP[category](search_query)
    elif category == "log_issue":
        tool_result = TOOL_MAP[category](question, user_id=session_id)
    else:
        tool_result = TOOL_MAP[category](question)

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
    for q in [
        "What causes E-322 and how do I fix it?",
        "What is NexaForge?",
        "Who is Narendra Modi?",
    ]:
        r = run_agent(q, session_id=f"test_{hash(q)}")
        print_chat_reply(q, r)