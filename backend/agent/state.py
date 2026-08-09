sessions = {}

def get_history(session_id):
    return sessions.get(session_id, [])

def add_exchange(session_id, question, answer):
    if session_id not in sessions:
        sessions[session_id] = []
    sessions[session_id].append({"question": question, "answer": answer})
    sessions[session_id] = sessions[session_id][-5:]  # keep last 5 exchanges only