from datetime import datetime
from typing import Any, Dict, List
from database.services.database_service import DatabaseService
from database.utils.logger import logger

# Sample products data
SAMPLE_PRODUCTS: List[Dict[str, Any]] = [
    {
        "product_id": "prod_001",
        "product_name": "Quantum X1 Pro Headphones",
        "brand": "AcousticLabs",
        "category": "Electronics",
        "description": "Active Noise Cancelling over-ear headphones with 40h battery life.",
        "price": 149.99,
        "discount_price": 129.99,
        "rating": 4.25,
        "total_reviews": 2,
        "availability": True,
        "image_url": "https://example.com/images/quantum_x1.jpg",
        "product_url": "https://example.com/products/quantum-x1-pro",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "product_id": "prod_002",
        "product_name": "ErgoComfort Ergonomic Chair",
        "brand": "ComfortPlus",
        "category": "Furniture",
        "description": "High-back ergonomic mesh office chair with lumbar support.",
        "price": 299.99,
        "discount_price": None,
        "rating": 1.0,
        "total_reviews": 1,
        "availability": True,
        "image_url": "https://example.com/images/ergo_chair.jpg",
        "product_url": "https://example.com/products/ergo-comfort-chair",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    },
    {
        "product_id": "prod_003",
        "product_name": "SmartFit Fitness Tracker v4",
        "brand": "WearTech",
        "category": "Wearables",
        "description": "Waterproof fitness tracker with heart rate and sleep monitoring.",
        "price": 79.99,
        "discount_price": 59.99,
        "rating": 0.0,
        "total_reviews": 0,
        "availability": True,
        "image_url": "https://example.com/images/smartfit_v4.jpg",
        "product_url": "https://example.com/products/smartfit-tracker-v4",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
]

# Sample reviews data
SAMPLE_REVIEWS: List[Dict[str, Any]] = [
    {
        "review_id": "rev_101",
        "product_id": "prod_001",
        "reviewer_name": "Alice Smith",
        "review_title": "Excellent Sound Quality",
        "review_text": "These headphones offer amazing bass and overall clarity. The ANC works great in noisy areas. Highly recommend!",
        "rating": 5.0,
        "verified_purchase": True,
        "review_date": datetime.utcnow(),
        "helpful_votes": 12,
        "sentiment": "positive",
        "confidence_score": 0.98,
        "created_at": datetime.utcnow(),
    },
    {
        "review_id": "rev_102",
        "product_id": "prod_001",
        "reviewer_name": "Bob Jones",
        "review_title": "Decent, but tight fit",
        "review_text": "The audio profile is balanced, but the headband feels tight and gets uncomfortable after long periods.",
        "rating": 3.5,
        "verified_purchase": True,
        "review_date": datetime.utcnow(),
        "helpful_votes": 2,
        "sentiment": "neutral",
        "confidence_score": 0.75,
        "created_at": datetime.utcnow(),
    },
    {
        "review_id": "rev_103",
        "product_id": "prod_002",
        "reviewer_name": "Charlie Brown",
        "review_title": "Plastic snapped immediately",
        "review_text": "Extremely disappointed. The armrest snapped during assembly. Poor construction. Sending it back.",
        "rating": 1.0,
        "verified_purchase": False,
        "review_date": datetime.utcnow(),
        "helpful_votes": 0,
        "sentiment": "negative",
        "confidence_score": 0.99,
        "created_at": datetime.utcnow(),
    }
]

# Sample sentiments data
SAMPLE_SENTIMENTS: List[Dict[str, Any]] = [
    {
        "review_id": "rev_101",
        "sentiment": "positive",
        "positive_score": 0.95,
        "neutral_score": 0.04,
        "negative_score": 0.01,
        "compound_score": 0.88,
        "confidence_score": 0.98,
        "analyzed_at": datetime.utcnow(),
    },
    {
        "review_id": "rev_102",
        "sentiment": "neutral",
        "positive_score": 0.35,
        "neutral_score": 0.50,
        "negative_score": 0.15,
        "compound_score": 0.20,
        "confidence_score": 0.75,
        "analyzed_at": datetime.utcnow(),
    },
    {
        "review_id": "rev_103",
        "sentiment": "negative",
        "positive_score": 0.01,
        "neutral_score": 0.09,
        "negative_score": 0.90,
        "compound_score": -0.85,
        "confidence_score": 0.99,
        "analyzed_at": datetime.utcnow(),
    }
]


class SeedService:
    """Service to handle populating database with mock development data and clearing collections."""

    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    def clear_database(self) -> None:
        """Truncates all products, reviews, and sentiments collections."""
        try:
            logger.info("Clearing existing collections before seeding...")
            prod_coll = self.db_service.products._get_coll()
            rev_coll = self.db_service.reviews._get_coll()
            sent_coll = self.db_service.sentiments._get_coll()

            p_del = prod_coll.delete_many({})
            r_del = rev_coll.delete_many({})
            s_del = sent_coll.delete_many({})

            logger.info(f"Cleared {p_del.deleted_count} products, {r_del.deleted_count} reviews, and {s_del.deleted_count} sentiments.")
        except Exception as e:
            logger.error(f"Error during clearing database collections: {e}")
            raise

    def seed_database(self) -> bool:
        """Seeds the database with sample products, reviews, and sentiments."""
        try:
            # 1. Clear database
            self.clear_database()

            # 2. Seed Products
            logger.info("Seeding products...")
            for prod in SAMPLE_PRODUCTS:
                self.db_service.insert_product(prod)

            # 3. Seed Reviews
            logger.info("Seeding reviews...")
            for rev in SAMPLE_REVIEWS:
                self.db_service.insert_review(rev)

            # 4. Seed Sentiments
            logger.info("Seeding sentiments...")
            for sent in SAMPLE_SENTIMENTS:
                self.db_service.insert_sentiment(sent)

            logger.info("Database Seeding Completed successfully.")
            return True
        except Exception as e:
            logger.error(f"Seeding failed: {e}")
            return False
