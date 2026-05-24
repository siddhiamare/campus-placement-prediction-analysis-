# backend/utils/db.py
# Lightweight JSON file-based storage
# In interviews: "I used a JSON file DB for simplicity;
# in production I'd swap this for PostgreSQL or MongoDB"

import json
import os
import uuid
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'db.json')


def _load() -> dict:
    """Load the entire database from disk."""
    if not os.path.exists(DB_PATH):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        return {"profiles": {}, "chats": {}}
    with open(DB_PATH, "r") as f:
        return json.load(f)


def _save(data: dict):
    """Persist the database to disk."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with open(DB_PATH, "w") as f:
        json.dump(data, f, indent=2)


# ── Profiles ──────────────────────────────────────────────────

def save_profile(user_id: str, profile: dict) -> str:
    """Save a prediction profile entry for a user."""
    data = _load()
    if user_id not in data["profiles"]:
        data["profiles"][user_id] = []

    entry = {**profile, "id": str(uuid.uuid4()), "saved_at": datetime.utcnow().isoformat()}
    data["profiles"][user_id].append(entry)

    # Keep only last 20 entries per user
    data["profiles"][user_id] = data["profiles"][user_id][-20:]
    _save(data)
    return entry["id"]


def get_profiles(user_id: str) -> list:
    """Get all saved profiles for a user."""
    data = _load()
    return data["profiles"].get(user_id, [])


def get_latest_profile(user_id: str) -> dict | None:
    """Get the most recent profile for a user."""
    profiles = get_profiles(user_id)
    return profiles[-1] if profiles else None


# ── Chat History ──────────────────────────────────────────────

def save_chat_message(session_id: str, role: str, content: str):
    """Append a chat message to a session."""
    data = _load()
    if "chats" not in data:
        data["chats"] = {}
    if session_id not in data["chats"]:
        data["chats"][session_id] = []

    data["chats"][session_id].append({
        "role":       role,
        "content":    content,
        "timestamp":  datetime.utcnow().isoformat(),
    })

    # Keep last 50 messages per session
    data["chats"][session_id] = data["chats"][session_id][-50:]
    _save(data)


def get_chat_history(session_id: str) -> list:
    """Get chat history for a session (messages only, no timestamps)."""
    data = _load()
    raw  = data.get("chats", {}).get(session_id, [])
    return [{"role": m["role"], "content": m["content"]} for m in raw]


def clear_chat(session_id: str):
    """Clear chat history for a session."""
    data = _load()
    if "chats" in data and session_id in data["chats"]:
        del data["chats"][session_id]
    _save(data)
