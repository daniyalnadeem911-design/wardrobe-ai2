import json
from flask import Blueprint, request, jsonify, session
from models.db import query
from services.weather_service import get_weather
from services.groq_service import generate_outfit
from utils.validators import friendly_error
from routes.wardrobe_routes import current_api_key

outfit_bp = Blueprint("outfit", __name__)

@outfit_bp.route("/api/outfit/generate", methods=["POST"])
def generate():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "not_onboarded"}), 401

    data = request.json
    occasion = data.get("occasion", "Casual")
    available_item_ids = data.get("available_item_ids", [])

    profile = query("SELECT * FROM users WHERE id=?", (user_id,), fetchone=True)
    weather = get_weather(profile.get("city"), profile.get("country"))

    all_items = query(
        "SELECT id, name, category, section, color, material, season FROM wardrobe WHERE user_id=?",
        (user_id,),
    )

    # NEW: restrict to only the pieces the user marked as available
    if available_item_ids:
        items = [i for i in all_items if i["id"] in available_item_ids]
    else:
        items = all_items

    if not items:
        return jsonify({"success": False, "error": "No available clothes selected. Add clothes or check some items."}), 400

    api_key = current_api_key(user_id)
    if not api_key:
        return jsonify({"success": False, "error": friendly_error("missing_api_key")}), 400

    try:
        result = generate_outfit(api_key, profile, weather, occasion, items)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": f"{type(e).__name__}: {e}"}), 500

    # (rest of the function stays exactly the same — outfit_id insert + outfit_items build)
    outfit_id = query(
        """INSERT INTO outfits (user_id, occasion, weather_summary, upper_id, lower_id,
           footwear_id, accessory_id, jacket_id, reasoning) VALUES (?,?,?,?,?,?,?,?,?)""",
        (
            user_id, occasion, json.dumps(weather),
            result.get("upper_id"), result.get("lower_id"), result.get("footwear_id"),
            result.get("accessory_id"), result.get("jacket_id"), json.dumps(result.get("reasoning", {})),
        ),
        commit=True,
    )

    outfit_items = []
    for key in ["upper_id", "lower_id", "footwear_id", "accessory_id", "jacket_id"]:
        item_id = result.get(key)
        if item_id:
            item = query("SELECT * FROM wardrobe WHERE id=?", (item_id,), fetchone=True)
            if item:
                item["reason"] = result.get("reasoning", {}).get(str(item_id), "")
                outfit_items.append(item)

    return jsonify({
        "success": True,
        "outfit_id": outfit_id,
        "weather": weather,
        "occasion": occasion,
        "overall_reasoning": result.get("overall_reasoning", ""),
        "items": outfit_items,
    })

@outfit_bp.route("/api/outfit/<int:outfit_id>/favorite", methods=["POST"])
def favorite(outfit_id):
    user_id = session.get("user_id")
    query("INSERT INTO favorites (user_id, outfit_id) VALUES (?,?)", (user_id, outfit_id), commit=True)
    return jsonify({"success": True})

@outfit_bp.route("/api/outfit/<int:outfit_id>/wear", methods=["POST"])
def mark_worn(outfit_id):
    user_id = session.get("user_id")
    query("INSERT INTO history (user_id, outfit_id) VALUES (?,?)", (user_id, outfit_id), commit=True)
    return jsonify({"success": True})

@outfit_bp.route("/api/history", methods=["GET"])
def history():
    user_id = session.get("user_id")
    rows = query(
        """SELECT h.worn_on, o.* FROM history h JOIN outfits o ON h.outfit_id = o.id
           WHERE h.user_id = ? ORDER BY h.worn_on DESC""",
        (user_id,),
    )
    return jsonify({"success": True, "history": rows})