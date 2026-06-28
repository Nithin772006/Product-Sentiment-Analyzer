def get_dummy_dashboard_data():
    """Return sample metrics for dashboard cards and charts."""
    return {
        "summary": {
            "totalReviews": 128,
            "averageRating": 4.1,
            "positivePercentage": 68,
            "neutralPercentage": 19,
            "negativePercentage": 13,
        },
        "sentimentDistribution": {
            "positive": 87,
            "neutral": 24,
            "negative": 17,
        },
        "ratingDistribution": {
            "1": 8,
            "2": 9,
            "3": 24,
            "4": 37,
            "5": 50,
        },
        "recentKeywords": ["battery", "quality", "delivery", "price", "comfort"],
    }
