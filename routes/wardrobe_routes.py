from flask import Blueprint, request, jsonify, session
from models.db import query
from services.image_service import save_upload, to_data_uri, cleanup_temp
from services.pdf_service import extract_pdf_text, extract_pdf_page_images
from services.groq_service import analyze_clothing_image, extract_articles_from_pdf_text
from utils.validators import allowed_image, allowed_pdf, friendly_error

wardrobe_bp = Blueprint("wardrobe", __name__)

def current_api_key(user_id):
    from config import Config
    user = query("SELECT groq_api_key FROM users WHERE id=?", (user_id,), fetchone=True)
    return (user and user.get("groq_api_key")) or Config.GROQ_API_KEY

@wardrobe_bp.route("/api/wardrobe/upload-image", methods=["POST"])
def upload_image():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "not_onboarded"}), 401

    file = request.files.get("image")
    if not file or not allowed_image(file.filename):
        return jsonify({"success": False, "error": friendly_error("invalid_image")}), 400

    api_key = current_api_key(user_id)
    if not api_key:
        return jsonify({"success": False, "error": friendly_error("missing_api_key")}), 400

    path = save_upload(file)
    try:
        analysis = analyze_clothing_image(api_key, path)
    except Exception as e:
        import traceback
        traceback.print_exc()
        cleanup_temp(path)
        return jsonify({"success": False, "error": friendly_error("detection_failed")}), 500

    # Converted to a compact data URI and stored straight in the database —
    # nothing is kept on local disk, so it survives every restart/redeploy.
    image_data = to_data_uri(path)
    cleanup_temp(path)

    item_id = query(
        """INSERT INTO wardrobe (user_id, name, category, section, color, material,
           pattern, sleeve_length, brand, season, description, image_path)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            user_id, analysis.get("name"), analysis.get("category"), analysis.get("section"),
            analysis.get("color"), analysis.get("material"), analysis.get("pattern"),
            analysis.get("sleeve_length"), analysis.get("brand"), analysis.get("season"),
            analysis.get("description"), image_data,
        ),
        commit=True,
    )
    return jsonify({"success": True, "item_id": item_id, "analysis": analysis})

@wardrobe_bp.route("/api/wardrobe/upload-pdf", methods=["POST"])
def upload_pdf():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "not_onboarded"}), 401

    file = request.files.get("pdf")
    if not file or not allowed_pdf(file.filename):
        return jsonify({"success": False, "error": friendly_error("invalid_pdf")}), 400

    api_key = current_api_key(user_id)
    if not api_key:
        return jsonify({"success": False, "error": friendly_error("missing_api_key")}), 400

    saved_ids = []
    try:
        text = extract_pdf_text(file)

        if text.strip():
            articles = extract_articles_from_pdf_text(api_key, text)
            for a in articles:
                item_id = query(
                    """INSERT INTO wardrobe (user_id, name, category, section, color, material, description)
                       VALUES (?,?,?,?,?,?,?)""",
                    (user_id, a.get("name"), a.get("category"), a.get("section"),
                     a.get("color"), a.get("material"), a.get("description")),
                    commit=True,
                )
                saved_ids.append(item_id)
        else:
            page_images = extract_pdf_page_images(file)
            for img_path in page_images:
                analysis = analyze_clothing_image(api_key, img_path)
                image_data = to_data_uri(img_path)
                cleanup_temp(img_path)
                item_id = query(
                    """INSERT INTO wardrobe (user_id, name, category, section, color, material,
                       pattern, sleeve_length, brand, season, description, image_path)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        user_id, analysis.get("name"), analysis.get("category"), analysis.get("section"),
                        analysis.get("color"), analysis.get("material"), analysis.get("pattern"),
                        analysis.get("sleeve_length"), analysis.get("brand"), analysis.get("season"),
                        analysis.get("description"), image_data,
                    ),
                    commit=True,
                )
                saved_ids.append(item_id)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": friendly_error("detection_failed")}), 500

    return jsonify({"success": True, "count": len(saved_ids), "item_ids": saved_ids})

@wardrobe_bp.route("/api/wardrobe", methods=["GET"])
def list_wardrobe():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "not_onboarded"}), 401

    search = request.args.get("search", "")
    category = request.args.get("category", "")
    color = request.args.get("color", "")

    sql = "SELECT * FROM wardrobe WHERE user_id = ?"
    params = [user_id]

    if search:
        sql += " AND (name LIKE ? OR color LIKE ? OR category LIKE ? OR material LIKE ?)"
        like = f"%{search}%"
        params += [like, like, like, like]
    if category:
        sql += " AND category = ?"
        params.append(category)
    if color:
        sql += " AND color = ?"
        params.append(color)

    sql += " ORDER BY created_at DESC"
    items = query(sql, tuple(params))
    return jsonify({"success": True, "items": items})

@wardrobe_bp.route("/api/wardrobe/<int:item_id>", methods=["PUT"])
def edit_item(item_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "not_onboarded"}), 401
    data = request.json
    fields = ["name", "category", "section", "color", "material", "pattern", "season", "description"]
    updates = ", ".join([f"{f} = ?" for f in fields if f in data])
    values = [data[f] for f in fields if f in data]
    values += [item_id, user_id]
    query(f"UPDATE wardrobe SET {updates} WHERE id = ? AND user_id = ?", tuple(values), commit=True)
    return jsonify({"success": True})

@wardrobe_bp.route("/api/wardrobe/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "not_onboarded"}), 401
    query("DELETE FROM wardrobe WHERE id = ? AND user_id = ?", (item_id, user_id), commit=True)
    return jsonify({"success": True})