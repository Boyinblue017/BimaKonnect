glossary_terms = {
    "premium": {
        "definition": "The amount of money you pay to an insurance company to maintain your insurance coverage.",
        "example": "You pay a monthly premium of 5,000 shillings for your health insurance."
    },
    "deductible": {
        "definition": "The amount you must pay out of your own pocket before the insurance company starts paying for covered expenses.",
        "example": "If your deductible is 500 shillings, you pay that amount first, then insurance covers the rest."
    },
    "beneficiary": {
        "definition": "A person designated to receive benefits from an insurance policy when a claim is made or in case of the policyholder's death.",
        "example": "You can name your spouse as the beneficiary of your life insurance policy."
    },
    "claim": {
        "definition": "A formal request to the insurance company to pay for a loss or expense covered by the insurance policy.",
        "example": "You file a claim after your car is damaged in an accident."
    },
    "underwriting": {
        "definition": "The process by which an insurance company evaluates the risk of insuring a person or property and decides whether to issue a policy.",
        "example": "During underwriting, the insurance company reviews your health history before approving your life insurance application."
    },
    "coverage": {
        "definition": "The protection provided by an insurance policy; the specific events or losses that the policy will pay for.",
        "example": "Your motor insurance coverage includes protection against theft and accidents."
    },
    "policy": {
        "definition": "A contract between you and an insurance company that outlines the terms, conditions, and coverage provided.",
        "example": "Your insurance policy details what is covered and for how long."
    },
    "liability": {
        "definition": "Legal responsibility for harm or damage caused to another person or their property.",
        "example": "If you accidentally damage someone's property, liability insurance covers the costs."
    },
    "exclusion": {
        "definition": "Specific situations or losses that are not covered by your insurance policy.",
        "example": "Your travel insurance policy may have an exclusion for high-risk activities like skydiving."
    },
    "co-insurance": {
        "definition": "A situation where both you and the insurance company share the costs of a covered loss in an agreed-upon percentage.",
        "example": "You pay 20% of medical costs while your insurance covers 80%."
    }
}


def get_glossary_term(term):
    """Get a specific glossary term"""
    term = term.lower()
    
    if term in glossary_terms:
        return {
            "term": term,
            "data": glossary_terms[term]
        }
    
    return {
        "error": f"Term '{term}' not found in glossary",
        "suggestion": "Try searching with a different term"
    }


def get_all_glossary_terms():
    """Get all glossary terms"""
    return glossary_terms


def search_glossary_terms(query):
    """Search glossary terms by keyword"""
    query = query.lower()
    results = []
    
    for term, data in glossary_terms.items():
        definition = data.get("definition", "").lower()
        example = data.get("example", "").lower()
        
        if query in term or query in definition or query in example:
            results.append({
                "term": term,
                "data": data
            })
    
    return results
