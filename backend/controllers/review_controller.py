from flask import jsonify

from services.review_service import get_dummy_reviews


def get_reviews():
    """Return placeholder reviews until scraping and database modules are ready."""
    return jsonify({"reviews": get_dummy_reviews()}), 200
