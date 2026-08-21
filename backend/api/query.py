import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter
from pydantic import BaseModel
from agent.run import run_agent
from storage import chat_store
import difflib

router = APIRouter()

class QueryRequest(BaseModel):
    question: str
    user_id: str = "guest"
    is_admin: bool = False  # Explicit flag from frontend

@router.get("/chat/history")
def get_chat_history(user_id: str):
    return chat_store.get_history(user_id)

@router.delete("/chat/history")
def clear_chat_history(user_id: str):
    chat_store.clear_history(user_id)
    return {"cleared": True}


# Known-good greeting spellings. This is just the seed list that fuzzy
# matching below compares against - not meant to be exhaustive by itself.
GREETINGS = [
    "hi", "hii", "hiii", "hello", "hey", "heyy",
    "good morning", "good evening", "good afternoon",
    "sup", "yo", "gm",
]


def is_greeting(raw_text: str) -> bool:
    """True if the message is an exact greeting OR close enough to one
    to be a likely typo (e.g. 'helo', 'hie', 'hlelo'). Only applies
    fuzzy matching to short messages (<= 2 words) so a real, longer
    manual question that happens to start with a greeting-ish word
    isn't accidentally swallowed by this shortcut."""
    text = raw_text.strip().lower()

    if text in GREETINGS:
        return True

    if len(text.split()) > 2:
        return False  # only fuzzy-match short, greeting-shaped messages

    close = difflib.get_close_matches(text, GREETINGS, n=1, cutoff=0.72)
    return bool(close)


@router.post("/query")
def query(req: QueryRequest):
    question = req.question.strip()

    # Catch greetings AND common typo variants (e.g. "helo", "hie",
    # "hiii") instantly, without spending a router/LLM call on them.
    if is_greeting(question):
        greeting_answer = (
            "Hi! I'm the NexaForge Maintenance Assistant. 🛠️\n\n"
            "I answer questions from your ingested equipment manuals — troubleshooting, "
            "error codes, and maintenance schedules. What do you need?" 
        )
        actual_role = "admin" if req.is_admin else "user"

        chat_store.save_message(req.user_id, actual_role, req.question)
        chat_store.save_message(req.user_id, "bot", greeting_answer, [])

        return {
            "answer": greeting_answer,
            "sources": [],
            "tool_used": None
        }

    # Standard role tracking
    actual_role = "admin" if req.is_admin else "user"

    # Save the human's question to the database
    chat_store.save_message(req.user_id, actual_role, req.question)

    # Run the AI agent
    result = run_agent(req.question, session_id=req.user_id)

    # Save the AI's response to the database
    chat_store.save_message(
        req.user_id,
        "bot",
        result.get("answer", ""),
        result.get("sources", []),
        result.get("tool_used")
    )

    return result