from flask import Blueprint, request, jsonify, session
from models.db import query

onboarding_bp = Blueprint("onboarding", __name__)

@onboarding_bp.route("/api/onboarding", methods=["POST"])
def save_profile():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "not_logged_in"}), 401

    data = request.json
    query(
        """UPDATE users SET gender=?, height=?, skin_tone=?, country=?, city=?,
           preferred_style=?, favorite_colors=?, onboarded=1 WHERE id=?""",
        (
            data.get("gender"), data.get("height"), data.get("skin_tone"),
            data.get("country"), data.get("city"), data.get("preferred_style"),
            ",".join(data.get("favorite_colors", [])), user_id,
        ),
        commit=True,
    )
    return jsonify({"success": True, "user_id": user_id})

@onboarding_bp.route("/api/profile", methods=["GET"])
def get_profile():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "no_profile"}), 404
    user = query("SELECT * FROM users WHERE id = ?", (user_id,), fetchone=True)
    return jsonify({"success": True, "profile": user})

@onboarding_bp.route("/api/profile", methods=["PUT"])
def update_profile():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "not_onboarded"}), 401

    data = request.json
    query(
        """UPDATE users SET gender=?, height=?, skin_tone=?, country=?, city=?,
           preferred_style=?, favorite_colors=? WHERE id=?""",
        (
            data.get("gender"), data.get("height"), data.get("skin_tone"),
            data.get("country"), data.get("city"), data.get("preferred_style"),
            ",".join(data.get("favorite_colors", [])), user_id,
        ),
        commit=True,
    )
    return jsonify({"success": True})