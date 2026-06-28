from flask import jsonify

from services.dashboard_service import get_dummy_dashboard_data


def get_dashboard():
    """Return placeholder dashboard metrics for frontend chart integration."""
    return jsonify(get_dummy_dashboard_data()), 200
