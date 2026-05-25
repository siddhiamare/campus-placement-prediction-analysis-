/* ============================================================
   PlaceMe – frontend/app.js
   All API calls go to the Flask backend (http://localhost:5000)
   ============================================================ */

const API_BASE = "/api";;   // ← change to your deployed URL in production

// ─── GLOBAL STATE ─────────────────────────────────────────────
const state = {
  year:             "2nd",
  lastProfile:      null,
  lastScore:        null,
  chatSessionId:    "session_" + Math.random().toString(36).slice(2, 10),
  interviewSession: "interview_" + Math.random().toString(36).slice(2, 10),
  userId:           "user_" + Math.random().toString(36).slice(2, 10),
  qNum:             1,
  interviewType:    "technical",
  targetCompany:    "product",
  candidateName:    "Candidate",
};

// ─── NAVIGATION ───────────────────────────────────────────────
function showPage(page, el) {
  document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));
  document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active"));
  document.getElementById("page-" + page).classList.add("active");
  if (el) el.classList.add("active");
  if (window.innerWidth <= 768) document.getElementById("sidebar").classList.remove("open");
}

function toggleSidebar() {
  document.getElementById("sidebar").classList.toggle("open");
}

function setYear(el, y) {
  state.year = y;
  document.querySelectorAll(".ytab").forEach(t => t.classList.remove("active"));
  el.classList.add("active");
}

function updateSlider(id, dispId, suffix, decimals) {
  const v = document.getElementById(id).value;
  document.getElementById(dispId).textContent = parseFloat(v).toFixed(parseInt(decimals || 0)) + suffix;
}

function toggleChip(el) { el.classList.toggle("on"); }

// ─── PREDICTOR ────────────────────────────────────────────────
async function runPredict() {
  const cgpa      = parseFloat(document.getElementById("cgpa").value);
  const ssc       = parseInt(document.getElementById("ssc").value);
  const hsc       = parseInt(document.getElementById("hsc").value);
  const backlogs  = parseInt(document.getElementById("backlogs").value);
  const intern    = parseInt(document.getElementById("intern").value);
  const projects  = parseInt(document.getElementById("projects").value);
  const cp        = parseInt(document.getElementById("cp").value);
  const skills    = document.querySelectorAll("#skillChips .chip.on").length;
  const skillNames= [...document.querySelectorAll("#skillChips .chip.on")].map(c => c.textContent.trim());

  // Show loading state on button
  const btn = document.querySelector("#page-predictor .btn-primary");
  btn.textContent = "Predicting…";
  btn.disabled = true;

  try {
    const res = await apiFetch("/predict", "POST", {
      cgpa, ssc, hsc, backlogs, intern, projects, cp,
      skills, skillNames,
      year:       state.year,
      userId:     state.userId,
      aiAnalysis: false,   // quick prediction first
    });

    state.lastProfile = { cgpa, ssc, hsc, backlogs, intern, projects, cp, skills, skillNames, year: state.year };
    state.lastScore   = { prob: res.probability, ...res.breakdown };

    renderResult(res);
  } catch (err) {
    alert("Prediction failed: " + err.message);
  } finally {
    btn.textContent = "→ Predict My Placement Chance";
    btn.disabled = false;
  }
}

function renderResult(res) {
  document.getElementById("emptyState").style.display    = "none";
  document.getElementById("resultContent").style.display = "block";

  const prob = res.probability;
  animateRing(prob);
  animateNum("scoreNum", prob, "%");

  const color = prob >= 70 ? "var(--green)" : prob >= 45 ? "var(--amber)" : "var(--red)";
  document.getElementById("scoreCircle").style.stroke = color;
  document.getElementById("scoreNum").style.color     = color;

  const vBox = document.getElementById("verdictBox");
  if (prob >= 70) {
    vBox.className   = "verdict-box good";
    vBox.textContent = "✓ High Placement Probability – Focus on interview preparation";
  } else if (prob >= 45) {
    vBox.className   = "verdict-box warn";
    vBox.textContent = "⚠ Moderate Chance – Target skill gaps and add more projects";
  } else {
    vBox.className   = "verdict-box bad";
    vBox.textContent = "✗ Needs Work – Start with CGPA improvement + DSA fundamentals";
  }

  const bd = res.breakdown;
  setTimeout(() => {
    setBar("barAcad", "barAcadPct", bd.academics);
    setBar("barTech", "barTechPct", bd.technical);
    setBar("barInd",  "barIndPct",  bd.industry);
  }, 150);

  // Render rule-based insights from backend
  const il = document.getElementById("insightsList");
  if (res.insights && res.insights.length) {
    il.innerHTML = res.insights.map(i =>
      `<div class="insight-item">
         <div class="insight-icon ${i.type === "good" ? "g" : i.type === "warn" ? "w" : "b"}">
           ${i.type === "good" ? "✓" : i.type === "warn" ? "!" : "✗"}
         </div>
         <div>${i.text}</div>
       </div>`
    ).join("");
  }
}

async function getAIAnalysis() {
  if (!state.lastProfile) return;
  showAILoadingInInsights();
  try {
    const res = await apiFetch("/predict", "POST", {
      ...state.lastProfile,
      skills:     state.lastProfile.skills,
      aiAnalysis: true,
      userId:     state.userId,
    });
    renderAIResponseInInsights(res.aiAnalysis || "No analysis returned.");
  } catch (e) {
    renderAIResponseInInsights("⚠ Could not reach Flask server. Make sure it's running on port 5000.");
  }
}

function showAILoadingInInsights() {
  document.getElementById("insightsList").innerHTML +=
    `<div class="ai-loading" id="aiInsightLoader"><div class="ai-spinner"></div> Getting full AI analysis from Flask…</div>`;
}

function renderAIResponseInInsights(text) {
  const loader = document.getElementById("aiInsightLoader");
  if (loader) loader.remove();
  const il = document.getElementById("insightsList");
  const lines = text.split("\n").filter(l => l.trim());
  il.innerHTML += lines.map(l =>
    `<div class="insight-item">
       <div class="insight-icon g" style="font-size:0.6rem">AI</div>
       <div>${l.replace(/^[•\-*]\s*/, "")}</div>
     </div>`
  ).join("");
}

// ─── CHAT ─────────────────────────────────────────────────────
async function sendChat() {
  const input = document.getElementById("chatInput");
  const msg   = input.value.trim();
  if (!msg) return;
  input.value  = "";
  input.style.height = "";
  appendChatMsg("user", msg);
  showTyping(true);

  try {
    const res = await apiFetch("/chat", "POST", {
      message:   msg,
      sessionId: state.chatSessionId,
      profile:   state.lastProfile ? { ...state.lastProfile, probability: state.lastScore?.prob } : null,
    });
    showTyping(false);
    appendChatMsg("ai", res.reply);
  } catch (e) {
    showTyping(false);
    appendChatMsg("ai", "⚠ Cannot reach Flask server. Make sure python app.py is running.");
  }
}

function sendQuick(text) {
  document.getElementById("chatInput").value = text;
  sendChat();
}

function appendChatMsg(role, text) {
  const isUser    = role === "user";
  const formatted = text.replace(/\n/g, "<br>").replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  document.getElementById("chatMessages").innerHTML +=
    `<div class="msg-row ${isUser ? "user" : ""}">
       ${!isUser ? '<div class="ai-avatar sm">AI</div>' : ""}
       <div class="chat-bubble ${isUser ? "user-bubble" : "ai-bubble"}">${formatted}</div>
     </div>`;
  const cw = document.getElementById("chatWindow");
  cw.scrollTop = cw.scrollHeight;
}

function showTyping(show) {
  document.getElementById("typingIndicator").style.display = show ? "flex" : "none";
  if (show) {
    const cw = document.getElementById("chatWindow");
    cw.scrollTop = cw.scrollHeight;
  }
}

// ─── RESUME ───────────────────────────────────────────────────
async function analyzeResume() {
  const text = document.getElementById("resumeText").value.trim();
  if (!text) { alert("Please paste your resume text first."); return; }

  const rr  = document.getElementById("resumeResult");
  rr.innerHTML = '<div class="ai-loading"><div class="ai-spinner"></div> Sending to Flask → Claude AI…</div>';

  try {
    const data = await apiFetch("/resume/analyze", "POST", { resumeText: text });
    renderResumeResult(data);
  } catch (e) {
    rr.innerHTML = `<div style="color:var(--red);padding:1rem">⚠ ${e.message}</div>`;
  }
}

function renderResumeResult(data) {
  const rr    = document.getElementById("resumeResult");
  const color = data.atsScore >= 70 ? "var(--green)" : data.atsScore >= 45 ? "var(--amber)" : "var(--red)";
  rr.innerHTML = `
    <div class="card-title">Resume Analysis</div>
    <div class="ats-score-row">
      <div class="ats-num" style="color:${color}">${data.atsScore}</div>
      <div><div style="font-weight:600;font-size:0.9rem">ATS Score</div><div class="ats-label">${data.verdict}</div></div>
    </div>
    <div class="resume-section"><h4>✓ Strengths</h4>
      ${data.strengths.map(s => `<div class="resume-bullet"><span class="rb-icon" style="color:var(--green)">✓</span>${s}</div>`).join("")}
    </div>
    <div class="resume-section"><h4>⚠ Improvements</h4>
      ${data.improvements.map(s => `<div class="resume-bullet"><span class="rb-icon" style="color:var(--amber)">!</span>${s}</div>`).join("")}
    </div>
    <div class="resume-section"><h4>✗ Missing</h4>
      ${data.missing.map(s => `<div class="resume-bullet"><span class="rb-icon" style="color:var(--red)">✗</span>${s}</div>`).join("")}
    </div>
    <div class="resume-section"><h4>Keywords to Add</h4>
      <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:4px">
        ${data.keywords.map(k => `<span style="background:var(--bg3);border:1px solid var(--border);padding:3px 10px;border-radius:6px;font-size:0.78rem;color:var(--accent)">${k}</span>`).join("")}
      </div>
    </div>
    <button class="btn-secondary" style="width:100%;margin-top:1rem" onclick="getResumeRewrite()">
      Ask Flask AI to Rewrite Weak Bullet Points
    </button>`;
}

async function getResumeRewrite() {
  const text = document.getElementById("resumeText").value.trim();
  const rr   = document.getElementById("resumeResult");
  rr.innerHTML += '<div class="ai-loading" id="rewriteLoader"><div class="ai-spinner"></div> Flask is generating improved bullets…</div>';

  try {
    const data = await apiFetch("/resume/rewrite", "POST", { resumeText: text });
    document.getElementById("rewriteLoader")?.remove();
    const bullets = data.rewrittenBullets || [];
    document.getElementById("resumeResult").innerHTML += `
      <div class="resume-section" style="margin-top:1rem"><h4>AI-Rewritten Bullet Points</h4>
        ${bullets.map(b => `<div class="resume-bullet"><span class="rb-icon" style="color:var(--accent)">★</span>${b.replace(/^\d+\.\s*/,"")}</div>`).join("")}
      </div>`;
  } catch (e) {
    document.getElementById("rewriteLoader")?.remove();
    alert("Rewrite failed: " + e.message);
  }
}

function loadSampleResume() {
  document.getElementById("resumeText").value =
`Rahul Sharma | rahul@email.com | +91-9876543210 | GitHub: github.com/rahulsharma

EDUCATION
B.Tech Computer Science – ABC Engineering College, Pune | 2021–2025
CGPA: 7.8/10 | 12th: 82% | 10th: 88%

SKILLS
Python, JavaScript, React.js, Node.js, MySQL, MongoDB, Git, REST APIs

EXPERIENCE
SDE Intern – XYZ Startup, Pune | May–July 2024
• Built REST APIs with Node.js and Express for user authentication module
• Worked on React frontend dashboard, reduced load time by 30%
• Fixed 15+ bugs and wrote unit tests using Jest

PROJECTS
1. Campus Placement Predictor (React, Flask, Python)
   • Predicts placement probability using weighted ML scoring
   • Integrated Claude AI for coaching, mock interviews, resume analysis
   • Deployed on Render with 200+ active users

2. E-Commerce Platform (React, Node.js, MongoDB)
   • Full-stack app with Razorpay payment integration
   • JWT authentication and admin panel
   • 45 GitHub stars

ACHIEVEMENTS
• Winner – College Hackathon 2024 (1st / 80 teams)
• 250+ LeetCode problems solved (Rating: 1650)
• AWS Cloud Practitioner Certified (2024)`;
}

// ─── MOCK INTERVIEW ───────────────────────────────────────────
async function startInterview() {
  const type    = document.getElementById("interviewType").value;
  const company = document.getElementById("targetCompany").value;
  const name    = document.getElementById("candidateName").value.trim() || "Candidate";

  state.interviewType    = type;
  state.targetCompany    = company;
  state.candidateName    = name;
  state.qNum             = 1;
  state.interviewSession = "interview_" + Math.random().toString(36).slice(2, 10);

  document.getElementById("interviewSetup").style.display   = "none";
  document.getElementById("interviewSession").style.display = "block";

  const typeLabels = { technical:"Technical Interview", hr:"HR Round", system:"System Design", full:"Full Round" };
  const compLabels = { product:"Product Company", service:"Service Company", startup:"Startup", mnc:"MNC" };
  document.getElementById("sessionTitle").textContent = `${compLabels[company]} – ${typeLabels[type]}`;
  document.getElementById("sessionSub").textContent   = `Question 1 of ~8 | Candidate: ${name}`;
  document.getElementById("interviewChat").innerHTML  = "";

  showInterviewTyping(true);
  try {
    const res = await apiFetch("/interview/start", "POST", {
      type, company, name, sessionId: state.interviewSession,
    });
    showInterviewTyping(false);
    appendInterviewMsg("ai", res.question);
  } catch (e) {
    showInterviewTyping(false);
    appendInterviewMsg("ai", "⚠ Cannot start interview. Is the Flask server running?");
  }
}

async function submitAnswer() {
  const input  = document.getElementById("interviewAnswer");
  const answer = input.value.trim();
  if (!answer) return;
  input.value  = "";
  input.style.height = "";

  appendInterviewMsg("user", answer);
  state.qNum++;
  document.getElementById("qCounter").textContent      = `Q${state.qNum}`;
  document.getElementById("sessionSub").textContent    = `Question ${state.qNum} of ~8 | Candidate: ${state.candidateName}`;

  showInterviewTyping(true);
  try {
    const res = await apiFetch("/interview/answer", "POST", {
      sessionId:   state.interviewSession,
      answer,
      type:        state.interviewType,
      company:     state.targetCompany,
      name:        state.candidateName,
      questionNum: state.qNum,
    });
    showInterviewTyping(false);
    appendInterviewMsg("ai", res.response, res.isFinal);
  } catch (e) {
    showInterviewTyping(false);
    appendInterviewMsg("ai", "⚠ Error: " + e.message);
  }
}

function appendInterviewMsg(role, text, isFinal) {
  const isUser    = role === "user";
  const formatted = text.replace(/\n/g, "<br>");
  document.getElementById("interviewChat").innerHTML +=
    `<div class="msg-row ${isUser ? "user" : ""}">
       ${!isUser ? '<div class="ai-avatar sm">IV</div>' : ""}
       <div class="chat-bubble ${isUser ? "user-bubble" : "ai-bubble"}" ${isFinal ? 'style="border-color:var(--green)"' : ""}>${formatted}</div>
     </div>`;
  const ic = document.getElementById("interviewChat");
  ic.scrollTop = ic.scrollHeight;
}

function showInterviewTyping(show) {
  const ic = document.getElementById("interviewChat");
  if (show) {
    ic.innerHTML += `<div id="interviewTyping" class="msg-row"><div class="ai-avatar sm">IV</div><div class="typing-dots"><span></span><span></span><span></span></div></div>`;
    ic.scrollTop = ic.scrollHeight;
  } else {
    document.getElementById("interviewTyping")?.remove();
  }
}

function endInterview() {
  document.getElementById("interviewSetup").style.display   = "block";
  document.getElementById("interviewSession").style.display = "none";
  document.getElementById("interviewChat").innerHTML        = "";
  state.qNum = 1;
}

// ─── ROADMAP ──────────────────────────────────────────────────
async function generateRoadmap() {
  const months   = document.getElementById("rmMonths").value;
  const weakArea = document.getElementById("rmWeak").value;
  const dailyHrs = document.getElementById("rmTime").value;
  const role     = document.getElementById("rmRole").value;

  const ro = document.getElementById("roadmapOutput");
  ro.innerHTML = '<div class="ai-loading"><div class="ai-spinner"></div> Flask is generating your personalized roadmap…</div>';

  try {
    const data = await apiFetch("/roadmap/generate", "POST", {
      months:     parseInt(months),
      weakArea,
      dailyHours: dailyHrs,
      role,
      cgpa:       state.lastProfile?.cgpa || null,
    });
    renderRoadmap(data);
  } catch (e) {
    ro.innerHTML = `<div style="color:var(--red);padding:1rem">⚠ ${e.message}</div>`;
  }
}

function renderRoadmap(data) {
  const ro = document.getElementById("roadmapOutput");
  ro.innerHTML = `
    <div class="card-title">${data.title || "Your Roadmap"}</div>
    ${data.summary ? `<p style="color:var(--muted);font-size:0.85rem;margin-bottom:1.25rem">${data.summary}</p>` : ""}
    <div class="timeline">
      ${(data.weeks || []).map((w, i) => `
        <div class="tl-item">
          <div class="tl-dot ${i === 0 ? "active" : ""}"></div>
          <div class="tl-week">${w.week}</div>
          <div class="tl-title">${w.theme}</div>
          <div class="tl-desc">${w.focus}</div>
          ${w.resources?.length ? `<div style="margin-top:6px;display:flex;flex-wrap:wrap;gap:5px">
            ${w.resources.map(r => `<span style="background:var(--bg3);border:1px solid var(--border);padding:2px 8px;border-radius:5px;font-size:0.72rem;color:var(--muted)">${r}</span>`).join("")}
          </div>` : ""}
          ${w.milestone ? `<div style="margin-top:6px;font-size:0.78rem;color:var(--green)">🎯 ${w.milestone}</div>` : ""}
        </div>`).join("")}
    </div>`;
}

// ─── API HELPER ────────────────────────────────────────────────
async function apiFetch(path, method = "GET", body = null) {
  const opts = {
    method,
    headers: { "Content-Type": "application/json" },
  };
  if (body) opts.body = JSON.stringify(body);

  const res  = await fetch(API_BASE + path, opts);
  const data = await res.json();

  if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
  return data;
}

// ─── ANIMATION HELPERS ────────────────────────────────────────
function animateRing(prob) {
  const circle = document.getElementById("scoreCircle");
  const offset = 314 - (prob / 100) * 314;
  setTimeout(() => { circle.style.strokeDashoffset = offset; }, 100);
}

function animateNum(id, target, suffix) {
  let cur  = 0;
  const el = document.getElementById(id);
  const iv = setInterval(() => {
    cur = Math.min(cur + Math.ceil(target / 25), target);
    el.textContent = cur + suffix;
    if (cur >= target) clearInterval(iv);
  }, 25);
}

function setBar(barId, pctId, pct) {
  document.getElementById(barId).style.width  = pct + "%";
  document.getElementById(pctId).textContent = pct + "%";
}

// ─── INIT ─────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  // Auto-resize chat textareas
  document.querySelectorAll("textarea").forEach(ta => {
    ta.addEventListener("input", function () {
      if (this.id === "chatInput" || this.id === "interviewAnswer") {
        this.style.height = "auto";
        this.style.height = Math.min(this.scrollHeight, 120) + "px";
      }
    });
  });

  // Check backend health on load
  fetch(API_BASE + "/health")
    .then(r => r.json())
    .then(() => {
      document.getElementById("apiStatus").innerHTML =
        '<span class="dot-pulse"></span> Flask API Connected';
    })
    .catch(() => {
      document.getElementById("apiStatus").innerHTML =
        '<span style="color:var(--red)">● Flask Offline</span>';
      document.getElementById("apiStatus").style.color = "var(--red)";
    });
});
