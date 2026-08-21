from flask import Blueprint, request, jsonify
try:
    from backend.services.recommendation_servce import recommend_insurance
except ModuleNotFoundError:
    from services.recommendation_servce import recommend_insurance

quiz_bp = Blueprint("quiz", __name__)


@quiz_bp.route("/recommend", methods=["POST"])
def recommend():
    profile = request.get_json(silent=True)
    if not isinstance(profile, dict):
        return jsonify({"error": "Please send your quiz answers."}), 400

    recommendations = recommend_insurance(profile)

    return jsonify({"recommendations": recommendations})
