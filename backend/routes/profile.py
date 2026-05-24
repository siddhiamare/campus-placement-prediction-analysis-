# backend/routes/profile.py
# GET  /api/profile/<user_id>         – get all saved profiles
# GET  /api/profile/<user_id>/latest  – get most recent profile
# DELETE /api/profile/<user_id>       – clear all profiles

from flask import Blueprint, jsonify
from utils.db import get_profiles, get_latest_profile, save_profile

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/<user_id>", methods=["GET"])
def get_all(user_id):
    profiles = get_profiles(user_id)
    return jsonify({"success": True, "profiles": profiles, "count": len(profiles)})


@profile_bp.route("/<user_id>/latest", methods=["GET"])
def get_latest(user_id):
    profile = get_latest_profile(user_id)
    if not profile:
        return jsonify({"success": False, "message": "No profiles found"}), 404
    return jsonify({"success": True, "profile": profile})
