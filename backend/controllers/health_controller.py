from flask import jsonify


def health_check():
    """Return a lightweight API health response."""
    return jsonify(
        {
            "status": "ok",
            "service": "Product Sentiment Analyzer API",
            "version": "1.0.0",
        }
    ), 200
