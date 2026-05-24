# backend/routes/interview.py
# POST /api/interview/start    – start a session, get first question
# POST /api/interview/answer   – submit answer, get next question or feedback

from flask import Blueprint, request, jsonify
from utils.ai_helper import call_claude
from utils.db        import save_chat_message, get_chat_history, clear_chat

interview_bp = Blueprint("interview", __name__)

COMPANY_CTX = {
    "product": "a top product company (Google / Microsoft / Amazon level). Focus on DSA (arrays, trees, DP, graphs), OOP, system design basics.",
    "service": "TCS, Infosys, Wipro, or Cognizant. Focus on aptitude logic, basic CS (OS, DBMS, CN), simple coding, and communication.",
    "startup": "a funded startup. Focus on practical skills, project experience, problem-solving attitude, and learning agility.",
    "mnc":     "Accenture, IBM, Capgemini, or Deloitte. Mix of technical basics, communication skills, and situational HR questions.",
}

TYPE_CTX = {
    "technical": "technical round — DSA problems, CS fundamentals (OS, DBMS, OOP, Networks), and project deep-dives.",
    "hr":        "HR round — self-introduction, strengths/weaknesses, career goals, situational questions, team fit.",
    "system":    "system design round — design scalable systems (URL shortener, Instagram feed, chat app, parking lot).",
    "full":      "complete interview: first 4 questions are technical (DSA + CS), then 4 HR questions.",
}


def build_system(interview_type, company, candidate_name):
    return f"""You are a professional placement interviewer from {COMPANY_CTX.get(company, COMPANY_CTX['product'])}
You are conducting a {TYPE_CTX.get(interview_type, TYPE_CTX['technical'])}
The candidate's name is {candidate_name}.

Rules:
1. Ask exactly ONE question per message. Never ask multiple questions at once.
2. After each answer: give 1-2 sentences of honest feedback (positive or constructive), then ask the next question.
3. Gradually increase difficulty as the interview progresses.
4. If the candidate says "I don't know" — give a brief hint and move on.
5. Be professional, firm but encouraging. Make it feel like a real interview.
6. When asked for final feedback (after all questions): give a detailed report — what went well, what to improve, overall rating out of 10, and 3 specific action items."""


@interview_bp.route("/start", methods=["POST"])
def start():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    interview_type  = data.get("type",      "technical")
    company         = data.get("company",   "product")
    candidate_name  = data.get("name",      "Candidate")
    session_id      = data.get("sessionId")

    if not session_id:
        return jsonify({"error": "sessionId required"}), 400

    # Clear any previous session with same ID
    clear_chat(session_id)

    system   = build_system(interview_type, company, candidate_name)
    messages = [{"role": "user", "content": "Start the interview. Greet the candidate briefly and ask the first question only."}]

    try:
        question = call_claude(messages=messages, system=system, max_tokens=400)
        save_chat_message(session_id, "user",      "Start the interview.")
        save_chat_message(session_id, "assistant", question)
        return jsonify({"success": True, "question": question, "sessionId": session_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@interview_bp.route("/answer", methods=["POST"])
def answer():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    session_id      = data.get("sessionId")
    user_answer     = data.get("answer", "").strip()
    interview_type  = data.get("type",    "technical")
    company         = data.get("company", "product")
    candidate_name  = data.get("name",    "Candidate")
    question_num    = int(data.get("questionNum", 1))

    if not session_id or not user_answer:
        return jsonify({"error": "sessionId and answer required"}), 400

    save_chat_message(session_id, "user", user_answer)
    history = get_chat_history(session_id)
    system  = build_system(interview_type, company, candidate_name)

    is_final = question_num >= 8

    if is_final:
        history.append({
            "role":    "user",
            "content": "The interview is now complete. Please provide a comprehensive feedback report."
        })

    try:
        response = call_claude(messages=history, system=system, max_tokens=600)
        save_chat_message(session_id, "assistant", response)
        return jsonify({
            "success":  True,
            "response": response,
            "isFinal":  is_final,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
