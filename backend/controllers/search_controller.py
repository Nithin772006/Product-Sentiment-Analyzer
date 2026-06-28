from flask import jsonify, request

from services.search_service import create_search_response


def search_product():
    """Accept a product search request and return placeholder search data."""
    payload = request.get_json(silent=True) or {}
    result = create_search_response(payload)
    return jsonify(result), 200
