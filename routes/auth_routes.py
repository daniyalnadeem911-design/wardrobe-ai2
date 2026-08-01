from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from models.db import query

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/api/signup", methods=["POST"])
def signup():
    data = request.json or {}
    username = (data.get("username") or "").strip().lower()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"success": False, "error": "Username and password are required."}), 400
    if len(password) < 6:
        return jsonify({"success": False, "error": "Password must be at least 6 characters."}), 400

    existing = query("SELECT id FROM users WHERE username = ?", (username,), fetchone=True)
    if existing:
        return jsonify({"success": False, "error": "That username is already taken."}), 400

    user_id = query(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, generate_password_hash(password)),
        commit=True,
    )
    session.permanent = True
    session["user_id"] = user_id
    return jsonify({"success": True, "user_id": user_id})


@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.json or {}
    username = (data.get("username") or "").strip().lower()
    password = data.get("password") or ""

    user = query("SELECT * FROM users WHERE username = ?", (username,), fetchone=True)
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"success": False, "error": "Wrong username or password."}), 401

    session.permanent = True
    session["user_id"] = user["id"]
    return jsonify({"success": True, "onboarded": bool(user.get("onboarded"))})


@auth_bp.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})