import os
from flask import Flask, render_template, session, redirect, url_for, Response
from config import Config
from models.db import init_db, query
from routes.auth_routes import auth_bp
from routes.onboarding_routes import onboarding_bp
from routes.wardrobe_routes import wardrobe_bp
from routes.outfit_routes import outfit_bp
from routes.settings_routes import settings_bp

app = Flask(__name__)
app.config.from_object(Config)

app.register_blueprint(auth_bp)
app.register_blueprint(onboarding_bp)
app.register_blueprint(wardrobe_bp)
app.register_blueprint(outfit_bp)
app.register_blueprint(settings_bp)

# Runs at import time now (not just under `python app.py`) so any
# production WSGI import (PythonAnywhere's WSGI file included) triggers it too.
init_db()


@app.context_processor
def inject_theme():
    # v10: makes the logged-in user's SAVED theme available to every template
    # as `page_theme`, so base.html can put "dark" on <body> before the page
    # even renders. This is the actual fix for dark mode resetting on every
    # page — the old code never looked at the saved value, only the OS setting.
    theme = "light"
    user_id = session.get("user_id")
    if user_id:
        user = query("SELECT theme FROM users WHERE id=?", (user_id,), fetchone=True)
        if user and user.get("theme"):
            theme = user["theme"]
    return {"page_theme": theme}


@app.route("/robots.txt")
def robots():
    content = "User-agent: *\nAllow: /\nAllow: /login\nAllow: /signup\nDisallow: /dashboard\nDisallow: /wardrobe\nDisallow: /generate-outfit\nDisallow: /history\nDisallow: /settings\nSitemap: https://daniyal11223344.pythonanywhere.com/sitemap.xml"
    return Response(content, mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap():
    content = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://daniyal11223344.pythonanywhere.com/</loc></url>
  <url><loc>https://daniyal11223344.pythonanywhere.com/login</loc></url>
  <url><loc>https://daniyal11223344.pythonanywhere.com/signup</loc></url>
</urlset>'''
    return Response(content, mimetype="application/xml")


@app.route("/")
def home():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return render_template("home.html")


@app.route("/signup")
def signup_page():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return render_template("signup.html")


@app.route("/login")
def login_page():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/onboarding")
def onboarding():
    if not session.get("user_id"):
        return redirect(url_for("login_page"))
    return render_template("onboarding.html")


@app.route("/dashboard")
def dashboard():
    if not session.get("user_id"):
        return redirect(url_for("login_page"))
    return render_template("dashboard.html")


@app.route("/wardrobe")
def wardrobe_page():
    if not session.get("user_id"):
        return redirect(url_for("login_page"))
    return render_template("wardrobe.html")


@app.route("/generate-outfit")
def generate_outfit_page():
    if not session.get("user_id"):
        return redirect(url_for("login_page"))
    return render_template("generate_outfit.html")


@app.route("/outfit-result")
def outfit_result_page():
    if not session.get("user_id"):
        return redirect(url_for("login_page"))
    return render_template("outfit_result.html")


@app.route("/history")
def history_page():
    if not session.get("user_id"):
        return redirect(url_for("login_page"))
    return render_template("history.html")


@app.route("/settings")
def settings_page():
    if not session.get("user_id"):
        return redirect(url_for("login_page"))
    return render_template("settings.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)