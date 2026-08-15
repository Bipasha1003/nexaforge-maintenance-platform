import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter
from pydantic import BaseModel
from agent.run import run_agent
from storage import chat_store

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

@router.post("/query")
def query(req: QueryRequest):
    question = req.question.strip()
    user_lower = question.lower()

    # Catch all variations of greetings instantly (case-insensitive)
    greetings = ["hi", "hii", "hiii", "hello", "hey", "good morning", "good evening", "sup"]
    if user_lower in greetings:
        greeting_answer = (
    "Hello! I am your AI Maintenance Assistant for NexaForge. 🛠️\n\n"
    "I am connected directly to our equipment manuals database (including the CNC Mill X500, Cold Saw, Hydraulic Press, and factory floor flowcharts), "
    "as well as live maintenance schedules and active floor notices.\n\n"
    "How can I help you today? You can ask me about troubleshooting error codes, checking maintenance frequencies, "
    "or reviewing standard operating procedures."
)
        actual_role = "admin" if req.is_admin else "user"
        
        chat_store.save_message(req.user_id, actual_role, req.question)
        chat_store.save_message(req.user_id, "bot", greeting_answer, [], None)
        
        return {
            "answer": greeting_answer,
            "sources": [],
            "tool_used": None,
            "image_url": None
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