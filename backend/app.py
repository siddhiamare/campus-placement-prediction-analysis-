
import os
from flask import Flask, jsonify, send_from_directory
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

from routes.predict   import predict_bp
from routes.chat      import chat_bp
from routes.resume    import resume_bp
from routes.interview import interview_bp
from routes.roadmap   import roadmap_bp
from routes.profile   import profile_bp

# ── App setup ────────────────────────────────────────────────
app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend'),
    static_url_path='',
)

# ── CORS headers (manual, no flask-cors needed) ──────────────
@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"]  = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, DELETE, OPTIONS"
    return response

@app.route('/', defaults={'path': ''}, methods=["OPTIONS"])
@app.route('/<path:path>',             methods=["OPTIONS"])
def options_handler(path):
    return jsonify({}), 200

# ── Register Blueprints ──────────────────────────────────────
app.register_blueprint(predict_bp,   url_prefix="/api/predict")
app.register_blueprint(chat_bp,      url_prefix="/api/chat")
app.register_blueprint(resume_bp,    url_prefix="/api/resume")
app.register_blueprint(interview_bp, url_prefix="/api/interview")
app.register_blueprint(roadmap_bp,   url_prefix="/api/roadmap")
app.register_blueprint(profile_bp,   url_prefix="/api/profile")

# ── Health check ─────────────────────────────────────────────
@app.route("/api/health")
def health():
    return jsonify({
        "status":    "ok",
        "message":   "PlaceMe Flask API is running",
        "version":   "1.0.0",
        "endpoints": [
            "POST /api/predict",
            "POST /api/chat",
            "GET  /api/chat/<session_id>",
            "POST /api/resume/analyze",
            "POST /api/resume/rewrite",
            "POST /api/interview/start",
            "POST /api/interview/answer",
            "POST /api/roadmap/generate",
            "GET  /api/profile/<user_id>",
        ]
    })

# ── Serve frontend for all other routes ──────────────────────
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    target = os.path.join(app.static_folder, path)
    if path and os.path.exists(target):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")

# ── Start ────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "1") == "1"
    print(f"\n🚀 PlaceMe Flask server → http://localhost:{port}")
    print(f"   Health check → http://localhost:{port}/api/health\n")
    app.run(host="0.0.0.0", port=port, debug=debug)
