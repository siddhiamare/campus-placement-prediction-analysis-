# backend/utils/scorer.py
# Placement probability scoring algorithm
# Simulates logistic-regression style weighted scoring across 8 parameters

def compute_score(cgpa, ssc, hsc, backlogs, intern, projects, cp, skills, year):
    """
    Compute placement probability score.

    Parameters
    ----------
    cgpa     : float  (5.0 – 10.0)
    ssc      : int    (40 – 100)   percentage
    hsc      : int    (40 – 100)   percentage
    backlogs : int    (0=none, 1=one, 2=two, 3=three+)
    intern   : int    (0=none, 1=one, 2=multiple, 3=PPO)
    projects : int    (0=none, 1=1-2, 2=3-5, 3=5+)
    cp       : int    (0=inactive, 1=beginner, 2=intermediate, 3=advanced)
    skills   : int    count of selected tech skills
    year     : str    "2nd" | "3rd" | "Final"

    Returns
    -------
    dict with probability (int), breakdown (dict), insights (list)
    """

    # ── Academics (max 46 pts) ──────────────────────────────
    acad = 0.0
    acad += min(30.0, ((cgpa - 5.0) / 5.0) * 30.0)   # CGPA: 30 pts
    acad += min(8.0,  (ssc / 100.0) * 8.0)             # SSC:   8 pts
    acad += min(8.0,  (hsc / 100.0) * 8.0)             # HSC:   8 pts
    backlog_penalty = [0, 5, 10, 18][min(backlogs, 3)]
    acad -= backlog_penalty
    acad  = max(0.0, acad)

    # ── Technical (max 32 pts) ──────────────────────────────
    tech = 0.0
    tech += min(20.0, skills * 3.2)                     # Skills: 20 pts
    tech += [0, 3, 8, 12][min(cp, 3)]                   # CP:     12 pts
    tech  = max(0.0, min(32.0, tech))

    # ── Industry Readiness (max 30 pts) ─────────────────────
    ind  = 0.0
    ind += [0, 8, 14, 18][min(intern, 3)]               # Internship: 18 pts
    ind += [0, 4,  9, 12][min(projects, 3)]             # Projects:   12 pts
    ind  = max(0.0, min(30.0, ind))

    # ── Final probability ────────────────────────────────────
    MAX_SCORE = 46.0 + 32.0 + 30.0   # 108
    raw_total = acad + tech + ind
    prob      = round((raw_total / MAX_SCORE) * 100)

    if year == "Final":
        prob = min(100, prob + 5)       # slight bonus for final year

    prob = max(5, min(97, prob))        # clamp to [5, 97]

    # ── Breakdown percentages ────────────────────────────────
    breakdown = {
        "academics": round((acad / 46.0) * 100),
        "technical": round((tech / 32.0) * 100),
        "industry":  round((ind  / 30.0) * 100),
    }

    # ── Rule-based insights ──────────────────────────────────
    insights = []

    if cgpa >= 8.0:
        insights.append({"type": "good", "text": "Excellent CGPA — most companies shortlist 7.5+. You're in a strong position."})
    elif cgpa >= 7.0:
        insights.append({"type": "warn", "text": f"CGPA {cgpa} is decent but some MNCs require 7.5+. Strong projects can compensate."})
    else:
        insights.append({"type": "bad",  "text": "Low CGPA reduces shortlisting chances. Focus on projects and skills to stand out."})

    if backlogs > 0:
        insights.append({"type": "bad",  "text": f"{backlogs} active backlog(s) — many campus drives disqualify you. Clear them immediately."})
    else:
        insights.append({"type": "good", "text": "Clean academic record — no backlog restrictions apply."})

    if intern >= 2:
        insights.append({"type": "good", "text": "Multiple internships significantly boost recruiter confidence in your profile."})
    elif intern == 1:
        insights.append({"type": "warn", "text": "One internship is good. A 2nd or a strong personal project will strengthen further."})
    else:
        insights.append({"type": "bad",  "text": "No internship experience — build 2–3 deployed projects to compensate."})

    if skills >= 4:
        insights.append({"type": "good", "text": f"{skills} skills selected. Ensure you have deep expertise in at least 2 of them."})
    elif skills >= 2:
        insights.append({"type": "warn", "text": f"Only {skills} skills — add 2 more relevant tech skills for better positioning."})
    else:
        insights.append({"type": "bad",  "text": "Very few skills — recruiters expect DSA + at least one full tech stack."})

    if cp >= 2:
        insights.append({"type": "good", "text": "CP experience will help in online assessment rounds at most product companies."})
    else:
        insights.append({"type": "warn", "text": "Solve 2–3 LeetCode problems daily to prepare for OA rounds."})

    return {
        "probability": prob,
        "breakdown":   breakdown,
        "insights":    insights,
    }
