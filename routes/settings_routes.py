import json
from flask import Blueprint, request, jsonify, session
from models.db import query

settings_bp = Blueprint("settings", __name__)

@settings_bp.route("/api/settings/theme", methods=["POST"])
def set_theme():
    user_id = session.get("user_id")
    theme = request.json.get("theme", "light")
    query("UPDATE users SET theme=? WHERE id=?", (theme, user_id), commit=True)
    return jsonify({"success": True})

@settings_bp.route("/api/settings/api-key", methods=["POST"])
def set_api_key():
    user_id = session.get("user_id")
    key = request.json.get("api_key", "")
    query("UPDATE users SET groq_api_key=? WHERE id=?", (key, user_id), commit=True)
    return jsonify({"success": True})

@settings_bp.route("/api/settings/export", methods=["GET"])
def export_wardrobe():
    user_id = session.get("user_id")
    items = query("SELECT * FROM wardrobe WHERE user_id=?", (user_id,))
    return jsonify({"success": True, "wardrobe": items})

@settings_bp.route("/api/settings/import", methods=["POST"])
def import_wardrobe():
    user_id = session.get("user_id")
    items = request.json.get("wardrobe", [])
    for item in items:
        query(
            """INSERT INTO wardrobe (user_id, name, category, section, color, material,
               pattern, sleeve_length, brand, season, description)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (
                user_id, item.get("name"), item.get("category"), item.get("section"),
                item.get("color"), item.get("material"), item.get("pattern"),
                item.get("sleeve_length"), item.get("brand"), item.get("season"),
                item.get("description"),
            ),
            commit=True,
        )
    return jsonify({"success": True, "imported": len(items)})

@settings_bp.route("/api/settings/delete-wardrobe", methods=["DELETE"])
def delete_wardrobe():
    user_id = session.get("user_id")
    query("DELETE FROM wardrobe WHERE user_id=?", (user_id,), commit=True)
    return jsonify({"success": True})