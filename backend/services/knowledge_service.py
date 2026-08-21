import json
import os

data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "insurance_data.json")
with open(data_path, "r") as file:
    insurance_data = json.load(file)


def get_insurance_info(query):
    """Return a useful answer for natural, plain-language insurance questions.

    This is deliberately rules-based for the MVP: it is reliable, inexpensive to run,
    and never pretends to quote a policy or provide regulated financial advice.
    """
    normalized = " ".join(query.lower().replace("?", " ").split())
    swahili = any(word in normalized.split() for word in {"bima", "ni", "nini", "gari", "afya", "maisha", "shamba"})

    aliases = {
        "motor insurance": ("motor insurance", "car insurance", "vehicle insurance", "bima ya gari", "gari"),
        "health insurance": ("health insurance", "medical insurance", "health cover", "bima ya afya", "afya", "hospital"),
        "life insurance": ("life insurance", "life cover", "bima ya maisha", "maisha", "funeral"),
        "crop insurance": ("crop insurance", "farm insurance", "agricultural insurance", "bima ya kilimo", "shamba", "farmer"),
        "sme insurance": ("business insurance", "sme insurance", "shop insurance", "biashara", "business"),
    }

    for product, terms in aliases.items():
        if any(term in normalized for term in terms):
            if product == "sme insurance":
                return {
                    "topic": product,
                    "definition": "Business insurance helps protect a small business from risks such as property damage, theft, or liability to customers.",
                    "benefits": ["Helps protect stock and equipment", "Can cover customer injury liability", "Keeps your business resilient after an unexpected loss"],
                    "next_step": "Ask an insurer which risks, limits, waiting periods, and exclusions apply to your business.",
                }
            answer = dict(insurance_data[product])
            answer["topic"] = product
            answer["next_step"] = "Compare benefits, exclusions, limits, and the premium before you buy. A licensed insurer or agent can explain a specific policy."
            if swahili:
                answer["swahili_hint"] = "Unaweza kuuliza kwa Kiswahili—kwa mfano, ‘Bima ya afya ni nini?’"
            return answer

    if any(term in normalized for term in ("premium", "deductible", "claim", "beneficiary", "underwriting", "exclusion")):
        return {
            "topic": "insurance term",
            "definition": "That is an important insurance term. Open the glossary below for a simple definition and example.",
            "benefits": [],
            "next_step": "Try searching the glossary for the exact word.",
        }

    return {
        "topic": "general insurance",
        "definition": "Insurance is a way to share the cost of unexpected losses. You pay a premium, and the insurer may pay covered losses under the policy terms.",
        "benefits": ["Helps manage large unexpected costs", "Can protect your family, health, vehicle, farm, or business"],
        "next_step": "Try asking about health, motor, life, crop, or business insurance. This is education, not a policy quote or financial advice.",
    }

