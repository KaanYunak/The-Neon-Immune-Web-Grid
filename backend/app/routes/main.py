from flask import Blueprint, jsonify

main_bp = Blueprint("main", __name__)

@main_bp.route("/", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "message": "Neon Immune Web Grid core running"
    }), 200

