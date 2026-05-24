# backend/routes/roadmap.py
# POST /api/roadmap/generate  – AI-generated week-by-week study plan

import json
from flask import Blueprint, request, jsonify
from utils.ai_helper import call_claude

roadmap_bp = Blueprint("roadmap", __name__)

WEAK_LABELS = {
    "dsa":           "DSA / Problem Solving",
    "cs":            "CS Fundamentals (OS, DBMS, Computer Networks)",
    "projects":      "Projects / Portfolio",
    "aptitude":      "Aptitude / Verbal / Logical Reasoning",
    "communication": "Communication / Soft Skills",
}

ROLE_LABELS = {
    "sde":     "Software Developer (SDE)",
    "analyst": "Business / Data Analyst",
    "data":    "Data Scientist / ML Engineer",
    "devops":  "DevOps / Cloud Engineer",
}


@roadmap_bp.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    months     = int(data.get("months",  6))
    weak_area  = data.get("weakArea",   "dsa")
    daily_hrs  = data.get("dailyHours", "2")
    role       = data.get("role",       "sde")
    cgpa       = data.get("cgpa")       # optional context

    weak_label = WEAK_LABELS.get(weak_area, weak_area)
    role_label = ROLE_LABELS.get(role, role)
    num_weeks  = min(months * 2, 12)   # 2 weeks per month, max 12 entries

    context = f"CGPA: {cgpa}" if cgpa else "CGPA not specified"

    prompt = f"""You are a placement preparation expert for Indian engineering students.
Create a structured study roadmap in JSON format. Student info:
- Months until campus placement: {months}
- Weakest area to focus on: {weak_label}
- Daily study time available: {daily_hrs} hours/day
- Target role: {role_label}
- {context}

Return ONLY valid JSON (no markdown, no backticks):
{{
  "title": "<descriptive roadmap title>",
  "summary": "<2-sentence overview of the plan>",
  "weeks": [
    {{
      "week": "Week 1-2",
      "theme": "<short theme name>",
      "focus": "<2-3 sentence description of what to study and do>",
      "resources": ["<platform/resource name>", "<resource 2>"],
      "milestone": "<measurable end-of-period goal>"
    }}
  ]
}}

Generate exactly {num_weeks} week-entries covering all {months} months.
Be specific: mention real resources (LeetCode, GeeksForGeeks, GATE Overflow, Naukri Learning, IndiaBix, etc.).
Make milestones measurable (e.g. "Solve 50 LeetCode Easy problems", not "practice coding")."""

    try:
        raw   = call_claude(messages=[{"role": "user", "content": prompt}], max_tokens=1500)
        clean = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(clean)
        return jsonify({"success": True, **result})
    except json.JSONDecodeError:
        return jsonify({"error": "AI returned invalid JSON. Please retry.", "raw": raw}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
