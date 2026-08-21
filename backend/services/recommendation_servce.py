def recommend_insurance(profile):
    """Give transparent educational recommendations, not quotes or policy advice."""
    recommendations = []

    def add(name, reason, priority):
        recommendations.append({"name": name, "reason": reason, "priority": priority})

    if profile.get("health") or profile.get("dependents"):
        add("Health insurance", "Helps with eligible medical expenses and unexpected hospital bills.", "Start here")
    if profile.get("vehicle"):
        add("Motor insurance", "Can protect against accident, theft, and third-party liability risks.", "Recommended")
    if profile.get("farmer"):
        add("Crop insurance", "Can help protect farm income from weather and other covered crop losses.", "Recommended")
    if profile.get("business"):
        add("SME insurance", "Can help protect stock, equipment, premises, and liability risks.", "Recommended")
    if profile.get("dependents"):
        add("Life insurance", "Can provide financial support for the people who rely on your income.", "Consider")

    if not recommendations:
        add("Health insurance", "Health costs are a common unexpected expense; compare suitable cover first.", "Start here")

    return recommendations
