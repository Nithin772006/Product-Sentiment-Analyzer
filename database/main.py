import sys
from pathlib import Path

# Add project root directory to python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from database.config.database import DatabaseManager
from database.config.settings import Settings
from database.scripts.create_indexes import create_all_indexes
from database.utils.logger import logger


def run_diagnostics() -> bool:
    """Verifies connection to MongoDB Atlas, runs index creations, and checks collection status."""
    try:
        logger.info("Initializing Database diagnostics...")

        # 1. Test database connection
        db = DatabaseManager.get_db()
        if db is None:
            logger.error("Could not establish a database connection. Please check database/.env")
            return False

        # Ping database
        client = DatabaseManager.get_client()
        client.admin.command("ping")
        logger.info(f"Database connection active. Database selected: '{Settings.DATABASE_NAME}'")

        # 2. Create indexes
        logger.info("Ensuring database indexes are created...")
        index_success = create_all_indexes()
        if not index_success:
            logger.warning("Index creation process reported errors.")

        # 3. Print collection stats
        logger.info("Checking collections statistics...")
        collections_to_check = [
            Settings.PRODUCTS_COLLECTION,
            Settings.REVIEWS_COLLECTION,
            Settings.SENTIMENTS_COLLECTION,
        ]

        for coll_name in collections_to_check:
            coll = db[coll_name]
            count = coll.count_documents({})
            logger.info(f"Collection '{coll_name}' exists with {count} documents.")

        logger.info("Diagnostics completed successfully.")
        return True
    except Exception as e:
        logger.critical(f"Database diagnostics failed with fatal error: {e}")
        return False


if __name__ == "__main__":
    logger.info("Starting Product Sentiment Analyzer Database Layer...")
    success = run_diagnostics()
    sys.exit(0 if success else 1)
