def recommend_insurance(profile):

    recommendations = []

    if profile.get("vehicle"):
        recommendations.append("Motor Insurance")

    if profile.get("farmer"):
        recommendations.append("Crop Insurance")

    if profile.get("business"):
        recommendations.append("SME Insurance")

    if profile.get("dependents"):
        recommendations.append("Life Insurance")

    if not recommendations:
        recommendations.append("Health Insurance")

    return recommendations