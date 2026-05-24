# backend/routes/chat.py
# POST /api/chat        – send a message, get AI reply
# GET  /api/chat/<sid>  – get history for a session
# DELETE /api/chat/<sid>– clear session

from flask import Blueprint, request, jsonify
from utils.ai_helper import call_claude
from utils.db        import save_chat_message, get_chat_history, clear_chat

chat_bp = Blueprint("chat", __name__)

COACH_SYSTEM = """You are PlaceMe AI Coach — an expert campus placement advisor for Indian engineering students (CS/IT branch).
You help students crack placement drives at companies like TCS, Infosys, Wipro, Accenture, Cognizant, Amazon, Microsoft, Google, Flipkart, and startups.
Give specific, actionable advice. Reference real platforms: LeetCode, HackerRank, IndiaBix, PrepInsta, Internshala, LinkedIn.
Keep responses concise: 3-5 short paragraphs or bullet points. Be honest but encouraging.
Assume the student is from a Tier 2/3 engineering college in India unless told otherwise."""


@chat_bp.route("/", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "message field required"}), 400

    session_id  = data.get("sessionId", "default")
    user_message = data["message"].strip()
    profile      = data.get("profile")          # optional – from predictor

    if not user_message:
        return jsonify({"error": "message cannot be empty"}), 400

    # ── Build system prompt (optionally inject profile context) ──
    system = COACH_SYSTEM
    if profile:
        system += f"\n\nStudent's profile (from Predictor): CGPA {profile.get('cgpa')}, " \
                  f"Skills: {', '.join(profile.get('skillNames', [])) or 'not specified'}, " \
                  f"Placement probability: {profile.get('probability', 'unknown')}%."

    # ── Load history + append new user message ────────────────
    history = get_chat_history(session_id)
    history.append({"role": "user", "content": user_message})
    save_chat_message(session_id, "user", user_message)

    # ── Call Claude ───────────────────────────────────────────
    try:
        reply = call_claude(messages=history, system=system, max_tokens=800)
        save_chat_message(session_id, "assistant", reply)
        return jsonify({"success": True, "reply": reply, "sessionId": session_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@chat_bp.route("/<session_id>", methods=["GET"])
def get_history(session_id):
    history = get_chat_history(session_id)
    return jsonify({"success": True, "history": history, "count": len(history)})


@chat_bp.route("/<session_id>", methods=["DELETE"])
def clear_session(session_id):
    clear_chat(session_id)
    return jsonify({"success": True, "message": "Chat history cleared"})
