# backend/routes/resume.py
# POST /api/resume/analyze  – ATS score + rule-based feedback
# POST /api/resume/rewrite  – Template-based resume bullet rewriting

from flask import Blueprint, request, jsonify
from utils.ai_helper import _analyze_resume

resume_bp = Blueprint("resume", __name__)

# ── Keyword bank for ATS suggestions ─────────────────────────
ATS_KEYWORDS_BY_STACK = {
    "python":     ["REST API", "Flask/Django", "pandas", "unit testing", "CI/CD"],
    "java":       ["Spring Boot", "JPA/Hibernate", "Maven", "microservices", "JUnit"],
    "javascript": ["React", "Node.js", "REST API", "async/await", "Jest"],
    "sql":        ["PostgreSQL", "query optimization", "joins", "indexing", "transactions"],
    "default":    ["Git", "Agile", "REST API", "unit testing", "Linux", "Docker"],
}

REWRITE_TEMPLATES = [
    "Built a full-stack {domain} application using {tech}, reducing manual effort by 40% and serving 500+ users.",
    "Developed and deployed a {domain} module that improved {metric} performance by 30% through algorithmic optimization.",
    "Designed and implemented a RESTful API for {domain} with {tech}, achieving 99% uptime and sub-200ms response time.",
    "Automated {domain} workflow using {tech}, saving 5+ hours/week of manual work and eliminating human error.",
    "Collaborated in a team of 4 to build a {domain} system using Agile methodology, delivering all milestones on schedule.",
]

import random, re

def _detect_stack(text: str) -> str:
    text_lower = text.lower()
    for lang in ["python", "java", "javascript", "sql"]:
        if lang in text_lower:
            return lang
    return "default"

def _generate_bullets(resume_text: str) -> list:
    stack = _detect_stack(resume_text)
    tech_map = {
        "python": "Python/Flask",
        "java": "Java/Spring Boot",
        "javascript": "React/Node.js",
        "sql": "PostgreSQL",
        "default": "the tech stack",
    }
    domains = ["user authentication", "data analytics", "e-commerce", "inventory management", "task automation"]
    metrics = ["API response", "database query", "page load", "data processing"]
    
    bullets = []
    for template in random.sample(REWRITE_TEMPLATES, 3):
        bullet = template.format(
            domain=random.choice(domains),
            tech=tech_map[stack],
            metric=random.choice(metrics),
        )
        bullets.append(bullet)
    return bullets


@resume_bp.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    if not data or "resumeText" not in data:
        return jsonify({"error": "resumeText required"}), 400

    resume_text = data["resumeText"].strip()[:3000]
    if not resume_text:
        return jsonify({"error": "resumeText cannot be empty"}), 400

    analysis = _analyze_resume(resume_text)
    stack    = _detect_stack(resume_text)
    keywords = ATS_KEYWORDS_BY_STACK.get(stack, ATS_KEYWORDS_BY_STACK["default"])

    # Build strengths and improvements from feedback
    strengths    = [f["text"] for f in analysis["feedback"] if f["type"] == "good"]
    improvements = [f["text"] for f in analysis["feedback"] if f["type"] in ("bad", "warn")]
    missing      = []
    if "github" not in resume_text.lower():
        missing.append("GitHub profile link")
    if not any(w in resume_text.lower() for w in ["project", "built", "developed"]):
        missing.append("Projects section")
    if not any(w in resume_text.lower() for w in ["skill", "proficient", "familiar"]):
        missing.append("Technical Skills section")
    if not any(w in resume_text.lower() for w in ["intern", "experience", "worked"]):
        missing.append("Internship / Work Experience section")

    verdict = (
        "Strong resume with good fundamentals — a few tweaks will make it stand out."
        if analysis["score"] >= 70 else
        "Resume needs improvement in key areas — focus on projects and quantifiable achievements."
        if analysis["score"] >= 50 else
        "Resume requires significant work — add projects, skills, and links to boost your chances."
    )

    return jsonify({
        "success":      True,
        "atsScore":     analysis["score"],
        "verdict":      verdict,
        "strengths":    strengths[:3] or ["Resume submitted successfully for review."],
        "improvements": improvements[:3] or ["Consider adding more quantifiable achievements."],
        "missing":      missing[:3] or ["Looks complete — double-check formatting."],
        "keywords":     keywords[:4],
    })


@resume_bp.route("/rewrite", methods=["POST"])
def rewrite():
    data = request.get_json()
    if not data or "resumeText" not in data:
        return jsonify({"error": "resumeText required"}), 400

    resume_text = data["resumeText"].strip()[:2000]
    if not resume_text:
        return jsonify({"error": "resumeText cannot be empty"}), 400

    bullets = _generate_bullets(resume_text)
    return jsonify({"success": True, "rewrittenBullets": bullets})
