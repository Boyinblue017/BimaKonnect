from flask import Blueprint, request, jsonify
from services.glossary_service import get_glossary_term, get_all_glossary_terms, search_glossary_terms

glossary_bp = Blueprint("glossary", __name__)


@glossary_bp.route("/glossary", methods=["GET"])
def get_glossary():
    """Get all glossary terms"""
    terms = get_all_glossary_terms()
    return jsonify({
        "glossary": terms,
        "total_terms": len(terms)
    })


@glossary_bp.route("/glossary/<term>", methods=["GET"])
def get_term(term):
    """Get a specific glossary term"""
    result = get_glossary_term(term.lower())
    return jsonify(result)


@glossary_bp.route("/glossary/search", methods=["POST"])
def search_glossary():
    """Search for glossary terms"""
    data = request.get_json()
    query = data.get("query", "").lower()
    
    if not query:
        return jsonify({
            "error": "Search query is required"
        }), 400
    
    results = search_glossary_terms(query)
    return jsonify({
        "query": query,
        "results": results,
        "total_results": len(results)
    })
