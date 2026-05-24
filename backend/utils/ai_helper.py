# backend/utils/ai_helper.py
# Rule-based AI replacement — no API key required

import random

# ── Chat Coach ────────────────────────────────────────────────

COACH_RESPONSES = {
    "cgpa": [
        "A CGPA below 7.0 can be a filter at some companies, but don't panic. Build 2–3 strong projects and aim for internships. Companies like TCS and Infosys shortlist at 6.0+, while Amazon/Google typically require 7.5+.",
        "Your CGPA matters more for getting shortlisted than for clearing rounds. Focus on your DSA skills and projects — that's what interviewers actually test. Use LeetCode and GeeksForGeeks daily.",
    ],
    "internship": [
        "Internships are gold on your resume. Apply on Internshala, LinkedIn, and AngelList. Even unpaid internships count — they show recruiters you can work in a real environment. Aim for at least one before your final year.",
        "No internship yet? Build and deploy 2–3 real-world projects instead. Host them on GitHub, add a live demo link, and write about them on LinkedIn. Recruiters notice effort.",
    ],
    "dsa": [
        "For DSA, follow this order: Arrays → Strings → Linked Lists → Trees → Graphs → DP. Start with LeetCode Easy, then Medium. Target 150+ problems before placement season. Use NeetCode roadmap as your guide.",
        "Practice DSA on LeetCode and HackerRank daily — even 1 problem/day adds up. For service companies (TCS, Infosys), IndiaBix and PrepInsta have specific pattern questions.",
    ],
    "resume": [
        "Keep your resume to 1 page. Lead with education, then projects (with GitHub links), then skills, then experience. Quantify everything — 'reduced load time by 40%' beats 'improved performance'.",
        "Use a clean ATS-friendly resume format. Avoid tables and graphics — they confuse applicant tracking systems. Tools like Resume.io or Overleaf's LaTeX templates work great.",
    ],
    "interview": [
        "For technical interviews: think aloud, start with a brute force, then optimize. Ask clarifying questions before coding. Practice on LeetCode and mock interviews on Pramp or InterviewBit.",
        "HR interviews need preparation too. Prepare answers for: 'Tell me about yourself', 'Why this company?', 'Strengths/weaknesses', 'A time you failed'. Use the STAR method for behavioral questions.",
    ],
    "placement": [
        "Campus placement prep checklist: ✓ CGPA above cutoff ✓ 100+ LeetCode problems ✓ 2+ deployed projects ✓ Internship or strong personal work ✓ Resume reviewed ✓ Mock interviews done. Start 6 months early!",
        "For product companies (Amazon, Flipkart, Swiggy): focus on DSA and system design. For service companies (TCS, Wipro, Infosys): aptitude + basic coding + communication. Know which track you're targeting.",
    ],
    "skill": [
        "Top skills for placement in 2025: DSA (always), one web framework (React/Node or Django), SQL basics, Git/GitHub, and basic system design. Pick a stack and go deep rather than learning 10 things shallowly.",
        "Python and JavaScript are the most versatile languages for placements. Python for data/backend/scripting, JS for full-stack. Either gets you far. Focus on fundamentals over frameworks.",
    ],
    "default": [
        "Great question! Focus on these three things for placements: (1) Strong DSA fundamentals on LeetCode, (2) 2–3 real projects with live demos, (3) Apply early and apply widely — aim for 20+ companies.",
        "My advice: consistency beats intensity. 2 hours of focused prep daily for 6 months beats cramming in the final week. Track your progress on a spreadsheet and adjust weekly.",
        "Connect with seniors who got placed at your target companies. They'll give you the most accurate interview prep advice. LinkedIn is your best friend for this — reach out, most people are happy to help.",
        "Use the 80/20 rule: 80% of placement questions come from 20% of topics. For coding: arrays, trees, and dynamic programming. For CS: OS (processes/threads), DBMS (SQL queries), and OOP concepts.",
    ]
}

def _get_chat_reply(user_message: str, profile=None) -> str:
    msg = user_message.lower()
    
    for keyword, responses in COACH_RESPONSES.items():
        if keyword in msg:
            reply = random.choice(responses)
            if profile:
                cgpa = profile.get("cgpa")
                if cgpa and keyword == "cgpa":
                    reply = f"Based on your CGPA of {cgpa}: " + reply
            return reply
    
    # Context-aware default if profile provided
    if profile:
        prob = profile.get("probability", 50)
        cgpa = profile.get("cgpa", "N/A")
        skills = profile.get("skillNames", [])
        skill_str = ", ".join(skills[:3]) if skills else "not specified"
        return (
            f"Based on your profile (CGPA: {cgpa}, Skills: {skill_str}, "
            f"Placement probability: {prob}%), here's my advice: "
            + random.choice(COACH_RESPONSES["default"])
        )
    
    return random.choice(COACH_RESPONSES["default"])


# ── Predict AI Analysis ───────────────────────────────────────

def _get_predict_analysis(cgpa, ssc, hsc, backlogs, intern, projects, cp, skill_names, probability, year) -> str:
    lines = []

    # Company fit
    if probability >= 75:
        lines.append(f"• Strong profile ({probability}%) — you're competitive for product companies like Amazon, Flipkart, and mid-tier MNCs.")
    elif probability >= 55:
        lines.append(f"• Moderate profile ({probability}%) — well-suited for service companies (TCS, Infosys, Wipro, Capgemini) and mid-size tech firms.")
    else:
        lines.append(f"• Profile needs work ({probability}%) — focus on TCS, Infosys, and Cognizant as primary targets while improving skills.")

    # CGPA
    if cgpa >= 8.0:
        lines.append(f"• CGPA {cgpa} is excellent — you pass the shortlist filter for virtually all companies including top product firms.")
    elif cgpa >= 7.0:
        lines.append(f"• CGPA {cgpa} is decent — you qualify for most drives. Some premium companies require 7.5+, so compensate with strong projects.")
    else:
        lines.append(f"• CGPA {cgpa} may filter you out at some companies. Prioritize clearing any backlogs and build a strong project portfolio.")

    # Backlogs
    if backlogs > 0:
        lines.append(f"• {backlogs} active backlog(s) — this is your most urgent issue. Many companies disqualify candidates with backlogs. Clear them before placement season.")
    else:
        lines.append("• Clean academic record with no backlogs — this keeps all opportunities open for you.")

    # Internship / projects
    if intern == 0 and projects <= 1:
        lines.append("• KEY SKILL GAP: No internship and minimal projects — build 2 deployed projects immediately (e.g., a full-stack web app + one ML or data project). Host them on GitHub with a live demo.")
    elif intern == 0:
        lines.append("• No internship — your projects are a good substitute, but try to land at least one internship via Internshala or LinkedIn before final year.")
    elif projects <= 1:
        lines.append("• Few projects — supplement your internship with 1–2 personal projects to show initiative and breadth of skills.")
    else:
        lines.append("• Good internship/project experience — highlight quantifiable achievements in your resume (e.g., 'built X that reduced Y by Z%').")

    # CP / skills
    if cp <= 1:
        lines.append("• Improve competitive programming: solve 2 LeetCode problems daily focusing on Arrays, Trees, and DP — these cover 70% of OA rounds.")
    else:
        lines.append("• Solid CP background — keep practicing and explore system design concepts to stand out in interviews.")

    return "\n".join(lines)


# ── Roadmap Generator ─────────────────────────────────────────

ROADMAP_TEMPLATES = {
    "sde": {
        "themes": [
            ("Arrays & Strings", "Master the fundamentals of array manipulation, two-pointer, sliding window, and string processing. These appear in 60% of coding interviews.", ["LeetCode", "GeeksForGeeks"], "Solve 30 Easy LeetCode problems on arrays and strings"),
            ("Linked Lists & Stacks/Queues", "Implement common operations: reversal, merge, cycle detection. Practice stack and queue based problems.", ["LeetCode", "InterviewBit"], "Complete LeetCode Linked List study plan (20 problems)"),
            ("Trees & BST", "Binary trees traversals (inorder, preorder, postorder), BST operations, height, LCA. These are interview favorites.", ["LeetCode", "GeeksForGeeks"], "Solve 25 tree problems including 10 BST-specific"),
            ("Graphs & BFS/DFS", "Graph representations, BFS, DFS, topological sort, shortest path (Dijkstra). Practice on connected component problems.", ["LeetCode", "CSES Problem Set"], "Solve 20 graph problems including BFS/DFS and shortest path"),
            ("Dynamic Programming", "Start with 1D DP (Fibonacci, Climbing Stairs), move to 2D (Knapsack, LCS). DP is the hardest topic — start early.", ["LeetCode DP Study Plan", "Aditya Verma YouTube"], "Complete 20 DP problems from Easy to Medium"),
            ("CS Fundamentals", "Review OS concepts (processes, threads, deadlocks), DBMS (SQL, normalization, transactions), and OOP principles with code examples.", ["GATE Overflow", "TutorialsPoint", "InterviewBit"], "Complete 100 MCQs on OS + DBMS and write SQL queries for 15 problems"),
            ("Projects & System Design", "Build or polish a full-stack project. Write clean README with setup instructions. Learn basic system design: caching, load balancing, databases.", ["GitHub", "System Design Primer", "Naukri Learning"], "Deploy 1 full-stack project with live URL and GitHub repo"),
            ("Mock Interviews & Applications", "Appear for 3+ mock interviews on Pramp. Apply to 20+ companies. Update LinkedIn and resume. Practice behavioral questions using STAR method.", ["Pramp", "LinkedIn", "Naukri"], "Complete 5 mock interviews and apply to 25 companies"),
        ]
    },
    "analyst": {
        "themes": [
            ("SQL & Databases", "Master SQL queries: JOINs, GROUP BY, subqueries, window functions. These are tested in almost every analyst interview.", ["LeetCode SQL", "Mode Analytics SQL Tutorial"], "Solve 30 SQL problems on LeetCode and complete Mode tutorial"),
            ("Excel & Data Tools", "Learn Excel pivot tables, VLOOKUP, conditional formatting. Start with Google Sheets if Excel is unavailable.", ["Coursera Excel course", "YouTube tutorials"], "Build 3 Excel dashboards from sample datasets"),
            ("Python for Data Analysis", "Learn pandas, numpy, and matplotlib. Focus on data cleaning, aggregation, and visualization rather than ML.", ["Kaggle Python course", "Real Python"], "Complete Kaggle Python + Pandas micro-courses"),
            ("Statistics Basics", "Mean, median, mode, standard deviation, hypothesis testing basics, correlation vs. causation. These come up in interviews.", ["Khan Academy Statistics", "StatQuest YouTube"], "Complete Khan Academy Statistics unit and attempt 20 stat MCQs"),
            ("Business Case Analysis", "Practice analyzing business cases: identify metrics, draw insights, present recommendations. Review cases from MBB firms.", ["Case Interview resources", "PrepLounge"], "Solve 5 business cases and present them to a peer"),
            ("Visualization & Dashboards", "Learn Tableau or Power BI basics — build 2 dashboards from real datasets (Kaggle). Data storytelling is key.", ["Tableau Public", "Power BI tutorials", "Kaggle Datasets"], "Publish 1 dashboard on Tableau Public"),
            ("Resume & Aptitude", "Update resume highlighting data projects. Practice aptitude (number series, data interpretation, logical reasoning) for written tests.", ["IndiaBix", "Naukri Learning"], "Score 80%+ on 5 full-length aptitude mock tests"),
            ("Interviews & Applications", "Apply to analyst roles at Big 4 (Deloitte, EY), MNCs, and product companies. Practice case interviews and behavioral questions.", ["LinkedIn", "Glassdoor", "Naukri"], "Apply to 20 analyst roles and complete 3 mock interviews"),
        ]
    },
    "data": {
        "themes": [
            ("Python & ML Libraries", "Master numpy, pandas, scikit-learn. Build intuition before jumping to deep learning.", ["Kaggle", "fast.ai"], "Complete Kaggle's Python + ML micro-courses"),
            ("Statistics & Probability", "Bayesian thinking, probability distributions, hypothesis testing, A/B testing. Core to every data science role.", ["StatQuest YouTube", "Khan Academy"], "Complete statistics unit and solve 30 probability problems"),
            ("ML Algorithms", "Understand linear/logistic regression, decision trees, random forests, and SVM. Know when to use which.", ["Hands-on ML Book", "Scikit-learn docs"], "Implement 5 algorithms from scratch in Python"),
            ("Data Wrangling", "Clean messy datasets: handle nulls, outliers, encoding. Practice on Kaggle competitions.", ["Kaggle competitions", "Real-world datasets"], "Complete 2 Kaggle notebooks with full EDA and cleaning"),
            ("Deep Learning Basics", "Neural networks, backprop, CNNs for vision, RNNs for sequence. Use TensorFlow or PyTorch.", ["fast.ai course", "DeepLearning.AI"], "Build and train a CNN on MNIST or CIFAR-10"),
            ("Projects & Portfolio", "Build end-to-end ML projects: data → model → deployment. Host on GitHub, write a Medium post about it.", ["GitHub", "Heroku/Streamlit", "Medium"], "Deploy 1 ML model with a Streamlit or Flask UI"),
            ("SQL for Data Science", "Data scientists write a lot of SQL. Practice complex queries, window functions, and CTEs.", ["Mode SQL", "LeetCode SQL"], "Solve 25 SQL problems and complete Mode tutorial"),
            ("Interviews & Applications", "Practice ML interview questions, code ML algorithms without libraries, explain model choices. Apply on LinkedIn and Naukri.", ["Glassdoor ML questions", "LinkedIn"], "Complete 3 mock ML interviews and apply to 20 roles"),
        ]
    },
    "devops": {
        "themes": [
            ("Linux & Shell Scripting", "Master Linux commands, file permissions, processes, cron jobs, and bash scripting. DevOps runs on Linux.", ["Linux Journey", "OverTheWire Bandit"], "Complete Linux Journey beginner + intermediate sections"),
            ("Git & Version Control", "Advanced Git: branching strategies, rebasing, resolving conflicts, hooks. Contribute to an open-source project.", ["Pro Git Book", "GitHub"], "Create a branched project with PR workflow on GitHub"),
            ("Docker & Containers", "Build, run, and compose Docker containers. Understand images, volumes, networks, and Docker Compose.", ["Docker docs", "Play with Docker"], "Containerize a web app with Docker Compose (app + DB)"),
            ("CI/CD Pipelines", "Set up GitHub Actions or Jenkins pipeline: automated build, test, and deploy. This is the core DevOps skill.", ["GitHub Actions docs", "Jenkins tutorials"], "Build a CI/CD pipeline that auto-deploys on push"),
            ("Cloud Basics (AWS/GCP)", "Learn EC2, S3, IAM, VPC on AWS or equivalent GCP services. Get AWS Cloud Practitioner certification.", ["AWS Free Tier", "ACloudGuru", "AWS Skill Builder"], "Pass AWS Cloud Practitioner exam or complete 10 hands-on labs"),
            ("Kubernetes Fundamentals", "Pods, deployments, services, ConfigMaps, scaling. Deploy a multi-container app on Minikube.", ["Kubernetes docs", "KodeKloud", "Minikube"], "Deploy a 3-tier app on local Kubernetes cluster"),
            ("Monitoring & Logging", "Set up Prometheus + Grafana for metrics, ELK stack for logs. Learn alerting basics.", ["Prometheus docs", "Grafana tutorials"], "Set up monitoring dashboard for a running app"),
            ("Interviews & Applications", "Practice DevOps interview questions: infrastructure as code (Terraform), troubleshooting scenarios. Apply on LinkedIn and Naukri.", ["LinkedIn", "Glassdoor DevOps"], "Apply to 20 DevOps roles and complete 3 mock interviews"),
        ]
    },
}

WEAK_EXTRA = {
    "dsa": "Extra attention has been placed on DSA throughout this roadmap since it's your key focus area. Dedicate 60% of daily study time to algorithmic problem-solving.",
    "cs": "CS Fundamentals (OS, DBMS, CN) are heavily weighted here — these are tested in both written exams and technical interviews at service companies.",
    "projects": "Building real projects is the priority. Every phase includes a project milestone — deploy each one with a live URL for maximum resume impact.",
    "aptitude": "Aptitude preparation is woven throughout. Spend 30 minutes daily on IndiaBix and PrepInsta — consistency is more effective than cramming.",
    "communication": "Communication skills are addressed in every milestone. Record yourself answering mock interview questions and review the recordings critically.",
}

def _generate_roadmap(months, weak_area, daily_hrs, role, cgpa) -> dict:
    role_key = role if role in ROADMAP_TEMPLATES else "sde"
    themes = ROADMAP_TEMPLATES[role_key]["themes"]
    num_weeks = min(months * 2, 12)
    
    role_labels = {
        "sde": "Software Developer (SDE)",
        "analyst": "Business / Data Analyst",
        "data": "Data Scientist / ML Engineer",
        "devops": "DevOps / Cloud Engineer",
    }
    weak_labels = {
        "dsa": "DSA / Problem Solving",
        "cs": "CS Fundamentals",
        "projects": "Projects / Portfolio",
        "aptitude": "Aptitude / Logical Reasoning",
        "communication": "Communication / Soft Skills",
    }

    selected_themes = (themes * ((num_weeks // len(themes)) + 1))[:num_weeks]
    
    weeks = []
    for i, (theme, focus, resources, milestone) in enumerate(selected_themes):
        start_week = i * (months * 4 // num_weeks) + 1
        end_week   = (i + 1) * (months * 4 // num_weeks)
        weeks.append({
            "week":      f"Week {start_week}–{end_week}",
            "theme":     theme,
            "focus":     focus + f" Allocate {daily_hrs} hours/day to this phase.",
            "resources": resources,
            "milestone": milestone,
        })

    cgpa_note = f" (based on your CGPA of {cgpa})" if cgpa else ""
    weak_note = WEAK_EXTRA.get(weak_area, "")

    return {
        "title":   f"{months}-Month {role_labels.get(role_key, 'Placement')} Roadmap{cgpa_note}",
        "summary": (
            f"A structured {months}-month plan targeting {role_labels.get(role_key, 'placement')} roles, "
            f"focusing on '{weak_labels.get(weak_area, weak_area)}' as the primary improvement area. "
            f"With {daily_hrs} hours/day of focused study, this roadmap will prepare you for campus placements. "
            + weak_note
        ),
        "weeks": weeks,
    }


# ── Interview Bot ─────────────────────────────────────────────

TECHNICAL_QUESTIONS = [
    "Tell me about yourself and why you want to be a software engineer.",
    "What is the difference between an array and a linked list? When would you use each?",
    "Explain the concept of recursion with an example. What are its advantages and disadvantages?",
    "Write a function to reverse a string without using built-in reverse methods.",
    "What is Big-O notation? What's the time complexity of binary search?",
    "Explain the difference between stack and heap memory.",
    "What is object-oriented programming? Explain inheritance and polymorphism with examples.",
    "Describe a project you built. What was the most challenging part and how did you solve it?",
]

HR_QUESTIONS = [
    "Tell me about yourself in 2 minutes.",
    "Why do you want to work at this company specifically?",
    "What is your greatest strength and how has it helped you academically or professionally?",
    "Describe a situation where you faced a significant challenge. How did you handle it?",
    "Where do you see yourself in 5 years?",
    "What is your greatest weakness and what are you doing to improve it?",
    "Tell me about a time you worked in a team and faced a conflict. How was it resolved?",
    "Why should we hire you over other candidates?",
]

FEEDBACK_SNIPPETS = [
    "Good effort — you structured your answer well.",
    "Solid answer. Try to be more specific with examples next time.",
    "You covered the main points. Work on being more concise.",
    "Good thinking. Consider also mentioning time complexity or trade-offs.",
    "Nice response. Confidence in delivery will improve with more practice.",
    "That's a reasonable approach. In an interview, always clarify assumptions first.",
]

def _get_interview_question(session_history: list, interview_type: str, company: str, 
                             candidate_name: str, is_start: bool, is_final: bool, 
                             question_num: int, user_answer: str = None) -> str:
    if is_start:
        return (
            f"Hello {candidate_name}, welcome to your mock interview! "
            f"I'll be conducting a {'technical' if interview_type == 'technical' else interview_type} interview today. "
            f"We'll go through about 8 questions, gradually increasing in depth. "
            f"Feel free to think aloud — that's encouraged. Let's begin.\n\n"
            f"**Question 1:** {TECHNICAL_QUESTIONS[0] if interview_type != 'hr' else HR_QUESTIONS[0]}"
        )
    
    if is_final:
        # Generate feedback report
        strengths = random.sample([
            "clear communication style",
            "structured approach to problems",
            "good use of examples",
            "willingness to think through problems aloud",
            "solid understanding of fundamentals",
        ], 2)
        improvements = random.sample([
            "Practice time complexity analysis for every solution",
            "Use the STAR method more consistently for behavioral questions",
            "Work on more LeetCode Medium problems",
            "Research the company more deeply before interviews",
            "Be more concise — aim for focused 60-90 second answers",
        ], 3)
        rating = random.randint(5, 8)
        
        return (
            f"**Interview Complete! Here's your feedback, {candidate_name}:**\n\n"
            f"**Overall Rating: {rating}/10**\n\n"
            f"**What went well:**\n"
            f"• {strengths[0].capitalize()}\n"
            f"• {strengths[1].capitalize()}\n\n"
            f"**Areas to improve:**\n"
            f"• {improvements[0]}\n"
            f"• {improvements[1]}\n"
            f"• {improvements[2]}\n\n"
            f"**3 Action Items before your next interview:**\n"
            f"1. Solve 30 more LeetCode problems (focus on Trees and DP)\n"
            f"2. Prepare 5 structured STAR stories from your project/academic experience\n"
            f"3. Do 2 more mock interviews on Pramp this week\n\n"
            f"Keep going — consistency is what separates placed students from the rest!"
        )
    
    # Mid-interview: give feedback + next question
    q_pool = TECHNICAL_QUESTIONS if interview_type != "hr" else HR_QUESTIONS
    if interview_type == "full":
        q_pool = TECHNICAL_QUESTIONS if question_num <= 4 else HR_QUESTIONS
    
    next_q_idx = min(question_num, len(q_pool) - 1)
    next_question = q_pool[next_q_idx]
    feedback = random.choice(FEEDBACK_SNIPPETS)
    
    return (
        f"**Feedback on your answer:** {feedback}\n\n"
        f"**Question {question_num + 1}:** {next_question}"
    )


# ── Resume routes ─────────────────────────────────────────────

def _analyze_resume(text: str) -> dict:
    word_count = len(text.split())
    has_github = "github" in text.lower()
    has_linkedin = "linkedin" in text.lower()
    has_email = "@" in text
    has_projects = any(w in text.lower() for w in ["project", "built", "developed", "created"])
    has_skills = any(w in text.lower() for w in ["python", "java", "javascript", "sql", "react", "node"])
    
    score = 50
    feedback = []
    
    if word_count < 200:
        feedback.append({"type": "bad", "text": "Resume seems too short — add more detail to your projects and experience."})
        score -= 10
    elif word_count > 800:
        feedback.append({"type": "warn", "text": "Resume may be too long for a fresher — aim for 1 page (400–600 words)."})
        score -= 5
    else:
        feedback.append({"type": "good", "text": f"Good resume length ({word_count} words) — concise and readable."})
        score += 10

    if has_github:
        feedback.append({"type": "good", "text": "GitHub link found — great for showcasing your code."})
        score += 10
    else:
        feedback.append({"type": "bad", "text": "No GitHub link found — add it! Recruiters actively check GitHub profiles."})
        score -= 10

    if has_linkedin:
        feedback.append({"type": "good", "text": "LinkedIn profile linked — helps recruiters verify your background."})
        score += 5
    else:
        feedback.append({"type": "warn", "text": "Add your LinkedIn URL — it increases recruiter trust and visibility."})

    if has_projects:
        feedback.append({"type": "good", "text": "Projects section detected — make sure each project has a GitHub link and 1-line impact statement."})
        score += 10
    else:
        feedback.append({"type": "bad", "text": "No projects found — this is critical for freshers. Add 2–3 projects immediately."})
        score -= 15

    if has_skills:
        feedback.append({"type": "good", "text": "Technical skills section found — ensure skills match your target job descriptions."})
        score += 5
    else:
        feedback.append({"type": "warn", "text": "Add a clearly labeled Technical Skills section with languages, frameworks, and tools."})

    return {
        "score": min(95, max(30, score)),
        "feedback": feedback,
        "wordCount": word_count,
    }


# ── Public interface (mirrors original call_claude signature) ──

def call_claude(messages: list, system: str = None, max_tokens: int = 1000) -> str:
    """
    Rule-based replacement for Claude API calls.
    Routes based on system prompt context.
    """
    last_user_msg = ""
    for m in reversed(messages):
        if m.get("role") == "user":
            last_user_msg = m.get("content", "")
            break

    system_lower = (system or "").lower()
    msg_lower = last_user_msg.lower()

    # ── Roadmap generation ────────────────────────────────────
    if ("roadmap" in msg_lower or "study plan" in msg_lower or '"weeks"' in msg_lower
            or "months until campus placement" in msg_lower or ("weakest area" in msg_lower and "target role" in msg_lower)):
        import re, json
        months     = int(re.search(r'(\d+)\s*months? until', last_user_msg, re.I).group(1)) if re.search(r'(\d+)\s*months? until', last_user_msg, re.I) else 6
        weak_match = re.search(r'weakest area.*?:\s*([^\n,]+)', last_user_msg, re.I)
        weak_area  = "dsa"
        if weak_match:
            wl = weak_match.group(1).lower()
            if "cs " in wl or "fundamental" in wl: weak_area = "cs"
            elif "project" in wl: weak_area = "projects"
            elif "aptitude" in wl: weak_area = "aptitude"
            elif "communication" in wl: weak_area = "communication"
        role_match = re.search(r'target role.*?:\s*([^\n,]+)', last_user_msg, re.I)
        role = "sde"
        if role_match:
            rl = role_match.group(1).lower()
            if "analyst" in rl: role = "analyst"
            elif "data scien" in rl or "ml" in rl: role = "data"
            elif "devops" in rl or "cloud" in rl: role = "devops"
        hrs_match = re.search(r'(\d+)\s*hours?/day', last_user_msg, re.I)
        daily_hrs = hrs_match.group(1) if hrs_match else "2"
        cgpa_match = re.search(r'cgpa.*?(\d+\.?\d*)', last_user_msg, re.I)
        cgpa = cgpa_match.group(1) if cgpa_match else None
        result = _generate_roadmap(months, weak_area, daily_hrs, role, cgpa)
        return json.dumps(result)

    # ── Predict AI analysis ───────────────────────────────────
    if "placement advisor" in system_lower or "bullet point" in msg_lower or "cgpa:" in msg_lower:
        import re
        cgpa   = float(re.search(r'cgpa:\s*(\d+\.?\d*)', last_user_msg, re.I).group(1)) if re.search(r'cgpa:\s*(\d+\.?\d*)', last_user_msg, re.I) else 7.0
        prob   = int(re.search(r'(\d+)%\s*placement probability', last_user_msg, re.I).group(1)) if re.search(r'(\d+)%\s*placement probability', last_user_msg, re.I) else 60
        bl     = int(re.search(r'backlogs:\s*(\d+)', last_user_msg, re.I).group(1)) if re.search(r'backlogs:\s*(\d+)', last_user_msg, re.I) else 0
        intern = int(re.search(r'internships:\s*(\d+)', last_user_msg, re.I).group(1)) if re.search(r'internships:\s*(\d+)', last_user_msg, re.I) else 0
        proj   = int(re.search(r'projects:\s*(\d+)', last_user_msg, re.I).group(1)) if re.search(r'projects:\s*(\d+)', last_user_msg, re.I) else 0
        cp_lvl = int(re.search(r'cp level:\s*(\d+)', last_user_msg, re.I).group(1)) if re.search(r'cp level:\s*(\d+)', last_user_msg, re.I) else 0
        skills_match = re.search(r'tech skills:\s*([^\n]+)', last_user_msg, re.I)
        skills = [s.strip() for s in skills_match.group(1).split(',')] if skills_match else []
        year   = "Final"
        return _get_predict_analysis(cgpa, 0, 0, bl, intern, proj, cp_lvl, skills, prob, year)

    # ── Interview bot ─────────────────────────────────────────
    if "interviewer" in system_lower or "interview" in system_lower:
        is_start = "start the interview" in msg_lower
        is_final = "comprehensive feedback report" in msg_lower or "interview is now complete" in msg_lower
        
        interview_type = "technical"
        if "hr round" in system_lower: interview_type = "hr"
        elif "full interview" in system_lower or "complete interview" in system_lower: interview_type = "full"
        elif "system design" in system_lower: interview_type = "system"
        
        company = "product"
        if "tcs" in system_lower or "infosys" in system_lower or "service" in system_lower: company = "service"
        elif "startup" in system_lower: company = "startup"
        elif "accenture" in system_lower or "ibm" in system_lower: company = "mnc"
        
        # Extract candidate name from system prompt
        import re
        name_match = re.search(r"candidate's name is ([A-Za-z]+)", system or "")
        candidate_name = name_match.group(1) if name_match else "Candidate"
        
        # Count questions from history
        q_count = sum(1 for m in messages if m.get("role") == "assistant")
        
        user_answer = last_user_msg if not is_start else None
        
        return _get_interview_question(
            messages, interview_type, company, candidate_name,
            is_start, is_final, q_count, user_answer
        )

    # ── Default: Coach chat ───────────────────────────────────
    profile = None
    if "student's profile" in system_lower:
        profile = {}  # minimal profile indicator
    return _get_chat_reply(last_user_msg, profile)
