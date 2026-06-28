def create_search_response(payload):
    """Build a dummy search response using the incoming request payload."""
    product_name = payload.get("productName", "Sample Product")
    platform = payload.get("platform", "amazon")

    return {
        "message": "Search request received. Scraping is not implemented yet.",
        "query": {
            "productName": product_name,
            "platform": platform,
        },
        "job": {
            "id": "demo-search-job-001",
            "status": "queued",
        },
    }
