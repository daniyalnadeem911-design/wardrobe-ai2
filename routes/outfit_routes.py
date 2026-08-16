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

    # Only reason over items the user marked as currently available.
    # Empty selection = fall back to the full wardrobe.
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
    except Exception:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": friendly_error("internet_error")}), 500

    # v9: the AI now returns up to 3 ranked combinations under "outfits" instead of
    # one combination at the top level. This fallback keeps things working even if
    # the model ever slips back to the old single-object shape.
    raw_options = result.get("outfits") or (
        [result] if (result.get("upper_id") or result.get("lower_id")) else []
    )

    options = []
    for opt in raw_options[:3]:
        outfit_items = []
        for key in ["upper_id", "lower_id", "footwear_id", "accessory_id", "jacket_id"]:
            item_id = opt.get(key)
            if item_id:
                item = query("SELECT * FROM wardrobe WHERE id=?", (item_id,), fetchone=True)
                if item:
                    item["reason"] = opt.get("reasoning", {}).get(str(item_id), "")
                    outfit_items.append(item)
        options.append({
            "upper_id": opt.get("upper_id"),
            "lower_id": opt.get("lower_id"),
            "footwear_id": opt.get("footwear_id"),
            "accessory_id": opt.get("accessory_id"),
            "jacket_id": opt.get("jacket_id"),
            "reasoning": opt.get("reasoning", {}),
            "overall_reasoning": opt.get("overall_reasoning", ""),
            "items": outfit_items,
        })

    if not options:
        return jsonify({"success": False, "error": friendly_error("internet_error")}), 500

    # v9: NOTHING is saved to the database yet. Saving now happens only when the
    # user taps "Choose This Outfit" on one specific option — see /api/outfit/choose
    # below. This is the actual fix for "only one suggestion, no way to pick."
    return jsonify({
        "success": True,
        "weather": weather,
        "occasion": occasion,
        "options": options,
    })

@outfit_bp.route("/api/outfit/choose", methods=["POST"])
def choose():
    # v9 NEW ROUTE. Called once, when the user taps "Choose This Outfit" on one
    # of the (up to 3) options returned by /api/outfit/generate above. This is
    # where a row actually gets written to the `outfits` table.
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "not_onboarded"}), 401

    data = request.json
    occasion = data.get("occasion", "Casual")
    weather = data.get("weather", {})

    outfit_id = query(
        """INSERT INTO outfits (user_id, occasion, weather_summary, upper_id, lower_id,
           footwear_id, accessory_id, jacket_id, reasoning) VALUES (?,?,?,?,?,?,?,?,?)""",
        (
            user_id, occasion, json.dumps(weather),
            data.get("upper_id"), data.get("lower_id"), data.get("footwear_id"),
            data.get("accessory_id"), data.get("jacket_id"), json.dumps(data.get("reasoning", {})),
        ),
        commit=True,
    )
    return jsonify({"success": True, "outfit_id": outfit_id})

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