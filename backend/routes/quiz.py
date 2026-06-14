from flask import Blueprint, request, jsonify
from services.recommendation_service import recommend_insurance

quiz_bp = Blueprint("quiz", __name__)


@quiz_bp.route("/recommend", methods=["POST"])
def recommend():

    profile = request.get_json()

    recommendations = recommend_insurance(profile)

    return jsonify({
        "recommendations": recommendations
    })