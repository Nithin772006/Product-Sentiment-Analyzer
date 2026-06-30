import sys
from pathlib import Path

# Fix python path so we can import database package when executing script directly
db_path = Path(__file__).resolve().parent.parent
sys.path.append(str(db_path))
sys.path.append(str(db_path.parent))

import pymongo
from database.config.database import DatabaseManager
from database.config.settings import Settings
from database.utils.logger import logger


def create_all_indexes() -> bool:
    """Creates the necessary indexes on Products, Reviews, and Sentiments collections to ensure
    performance and enforce uniqueness constraints.
    """
    try:
        # Get collections
        prod_coll = DatabaseManager.get_collection(Settings.PRODUCTS_COLLECTION)
        rev_coll = DatabaseManager.get_collection(Settings.REVIEWS_COLLECTION)
        sent_coll = DatabaseManager.get_collection(Settings.SENTIMENTS_COLLECTION)

        if any(coll is None for coll in [prod_coll, rev_coll, sent_coll]):
            logger.error("Failed to acquire database collections. Ensure connection settings are correct.")
            return False

        logger.info("Initializing index creation...")

        # 1. Indexes for Products Collection
        logger.info("Creating indexes for products collection...")
        # Unique index on product_id
        prod_coll.create_index([("product_id", pymongo.ASCENDING)], unique=True)
        # Standard query performance indexes
        prod_coll.create_index([("product_name", pymongo.TEXT)])
        prod_coll.create_index([("brand", pymongo.ASCENDING)])
        prod_coll.create_index([("category", pymongo.ASCENDING)])
        prod_coll.create_index([("rating", pymongo.DESCENDING)])

        # 2. Indexes for Reviews Collection
        logger.info("Creating indexes for reviews collection...")
        # Unique index on review_id
        rev_coll.create_index([("review_id", pymongo.ASCENDING)], unique=True)
        # Standard query performance indexes
        rev_coll.create_index([("product_id", pymongo.ASCENDING)])
        rev_coll.create_index([("sentiment", pymongo.ASCENDING)])
        rev_coll.create_index([("rating", pymongo.DESCENDING)])

        # 3. Indexes for Sentiments Collection
        logger.info("Creating indexes for sentiments collection...")
        # Unique index on review_id (one sentiment analysis record per review)
        sent_coll.create_index([("review_id", pymongo.ASCENDING)], unique=True)
        # Standard query performance indexes
        sent_coll.create_index([("sentiment", pymongo.ASCENDING)])

        logger.info("Index Created successfully on all collections.")
        return True
    except Exception as e:
        logger.error(f"Error occurred during index creation: {e}")
        return False


if __name__ == "__main__":
    success = create_all_indexes()
    sys.exit(0 if success else 1)
