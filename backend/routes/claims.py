from flask import Blueprint, jsonify, request

try:
    from backend.services.claims_service import get_claim_guidance
except ModuleNotFoundError:
    from services.claims_service import get_claim_guidance


claims_bp = Blueprint("claims", __name__)


@claims_bp.route("/claims/guidance", methods=["POST"])
def claims_guidance():
    data = request.get_json(silent=True) or {}
    cover_type = str(data.get("cover_type", "")).strip().lower()
    incident = str(data.get("incident", "")).strip().lower()

    if not cover_type or not incident:
        return jsonify({"error": "Please choose a cover type and what happened."}), 400

    return jsonify(get_claim_guidance(cover_type, incident))
