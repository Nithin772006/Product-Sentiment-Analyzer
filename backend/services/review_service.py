def get_dummy_reviews():
    """Return sample review records that match the planned review data shape."""
    return [
        {
            "id": "rev-001",
            "productName": "Sample Wireless Headphones",
            "platform": "amazon",
            "rating": 5,
            "title": "Great sound quality",
            "reviewText": "The product feels premium and the battery lasts long.",
            "sentiment": "positive",
            "sentimentScore": 0.86,
        },
        {
            "id": "rev-002",
            "productName": "Sample Wireless Headphones",
            "platform": "amazon",
            "rating": 3,
            "title": "Average comfort",
            "reviewText": "Sound is good, but the ear cushions could be softer.",
            "sentiment": "neutral",
            "sentimentScore": 0.12,
        },
        {
            "id": "rev-003",
            "productName": "Sample Wireless Headphones",
            "platform": "amazon",
            "rating": 1,
            "title": "Stopped working",
            "reviewText": "The device stopped charging after a few days.",
            "sentiment": "negative",
            "sentimentScore": -0.72,
        },
    ]
