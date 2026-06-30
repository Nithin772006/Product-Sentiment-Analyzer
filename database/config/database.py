import sys
from pymongo import MongoClient
from pymongo.errors import (
    ConfigurationError,
    ConnectionFailure,
    OperationFailure,
)
from database.config.settings import Settings
from database.utils.logger import logger


class DatabaseManager:
    """Manages the MongoDB Atlas client connection singleton."""

    _client = None

    @classmethod
    def get_client(cls) -> MongoClient:
        """Initializes and returns the MongoClient instance if not already created."""
        if cls._client is None:
            try:
                # Log attempt
                logger.info(f"Connecting to MongoDB Atlas (Timeout: {Settings.CONNECTION_TIMEOUT_MS}ms)...")
                
                # Check for URI placeholder
                if "<username>" in Settings.MONGO_URI or "<password>" in Settings.MONGO_URI:
                    logger.warning("MONGO_URI still contains placeholder values. Connection might fail.")

                cls._client = MongoClient(
                    Settings.MONGO_URI,
                    serverSelectionTimeoutMS=Settings.CONNECTION_TIMEOUT_MS,
                    connectTimeoutMS=Settings.CONNECTION_TIMEOUT_MS,
                )
                # Force connection check using ping
                cls._client.admin.command("ping")
                logger.info("Database Connected successfully to MongoDB.")
            except ConfigurationError as e:
                logger.error(f"MongoDB Configuration Error (Check your connection string format): {e}")
                cls._client = None
            except ConnectionFailure as e:
                logger.error(f"MongoDB Connection Failure: {e}")
                cls._client = None
            except OperationFailure as e:
                logger.error(f"MongoDB Operation Failure (Auth error or permission issues): {e}")
                cls._client = None
            except Exception as e:
                logger.error(f"Unexpected MongoDB connection error: {e}")
                cls._client = None

        return cls._client

    @classmethod
    def get_db(cls):
        """Returns the database object or None if connection failed."""
        client = cls.get_client()
        if client is not None:
            return client[Settings.DATABASE_NAME]
        return None

    @classmethod
    def get_collection(cls, collection_name: str):
        """Returns a collection reference or None if connection failed."""
        db = cls.get_db()
        if db is not None:
            return db[collection_name]
        return None

    @classmethod
    def close_connection(cls):
        """Closes the client connection."""
        if cls._client is not None:
            cls._client.close()
            cls._client = None
            logger.info("MongoDB connection closed.")
