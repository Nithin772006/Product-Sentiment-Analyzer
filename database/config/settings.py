import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from database/.env
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    """Database configurations and settings."""

    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/product_sentiment_db")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "product_sentiment_db")

    # Collection names
    PRODUCTS_COLLECTION = os.getenv("PRODUCTS_COLLECTION", "products")
    REVIEWS_COLLECTION = os.getenv("REVIEWS_COLLECTION", "reviews")
    SENTIMENTS_COLLECTION = os.getenv("SENTIMENTS_COLLECTION", "sentiments")

    # Utilities configuration
    CONNECTION_TIMEOUT_MS = int(os.getenv("CONNECTION_TIMEOUT_MS", "5000"))
    LOGGING_ENABLED = os.getenv("LOGGING_ENABLED", "true").lower() == "true"
