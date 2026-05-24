# backend/routes/predict.py
# POST /api/predict  –  scoring + optional AI deep analysis

from flask import Blueprint, request, jsonify
from utils.scorer   import compute_score
from utils.ai_helper import call_claude
from utils.db        import save_profile

predict_bp = Blueprint("predict", __name__)


@predict_bp.route("/", methods=["POST"])
def predict():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    # ── Required fields ──────────────────────────────────────
    required = ["cgpa", "ssc", "hsc", "backlogs", "intern", "projects", "cp", "skills", "year"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    try:
        cgpa      = float(data["cgpa"])
        ssc       = int(data["ssc"])
        hsc       = int(data["hsc"])
        backlogs  = int(data["backlogs"])
        intern    = int(data["intern"])
        projects  = int(data["projects"])
        cp        = int(data["cp"])
        skills    = int(data["skills"])
        year      = str(data["year"])
        skill_names = data.get("skillNames", [])
        user_id     = data.get("userId")
        want_ai     = data.get("aiAnalysis", False)
    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Invalid field value: {e}"}), 400

    # ── Compute score ────────────────────────────────────────
    result = compute_score(cgpa, ssc, hsc, backlogs, intern, projects, cp, skills, year)

    # ── Save to DB ───────────────────────────────────────────
    if user_id:
        save_profile(user_id, {
            "cgpa": cgpa, "ssc": ssc, "hsc": hsc,
            "backlogs": backlogs, "intern": intern,
            "projects": projects, "cp": cp,
            "skills": skills, "skillNames": skill_names,
            "year": year, "probability": result["probability"],
        })

    # ── Optional AI deep analysis ────────────────────────────
    if want_ai:
        prompt = f"""You are a senior campus placement advisor at an IIT.
Student profile:
- Year: {year}, CGPA: {cgpa}, SSC: {ssc}%, HSC: {hsc}%
- Backlogs: {backlogs}, Internships: {intern} (0=none, 3=PPO/full-time offer)
- Projects: {projects} (0=none, 3=5+ projects), CP level: {cp} (0=inactive, 3=advanced)
- Tech Skills: {', '.join(skill_names) if skill_names else 'none specified'}
- Model prediction: {result['probability']}% placement probability

Give a concise, honest analysis in 5-6 bullet points. Be specific — mention actual company names suited to their profile (e.g. TCS for CGPA 6-7, Amazon for CGPA 8+). Mention exactly 1 key skill gap they must fix immediately. Plain text, no markdown headers."""

        try:
            ai_text = call_claude(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
            )
            result["aiAnalysis"] = ai_text
        except Exception as e:
            result["aiAnalysis"] = f"[AI unavailable: {str(e)}]"

    return jsonify({"success": True, **result})
