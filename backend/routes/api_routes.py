from flask import Blueprint

from controllers.dashboard_controller import get_dashboard
from controllers.health_controller import health_check
from controllers.review_controller import get_reviews
from controllers.search_controller import search_product


api_bp = Blueprint("api", __name__)

# Routes are intentionally thin; controller functions own request handling.
api_bp.get("/health")(health_check)
api_bp.post("/search")(search_product)
api_bp.get("/reviews")(get_reviews)
api_bp.get("/dashboard")(get_dashboard)
