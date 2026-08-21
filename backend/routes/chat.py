from flask import Blueprint, request, jsonify
from backend.services.knowledge_service import get_insurance_info

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    question = str(data.get("question", "")).strip()

    if not question:
        return jsonify({"error": "Please enter an insurance question."}), 400

    response = get_insurance_info(question)

    return jsonify(response)
