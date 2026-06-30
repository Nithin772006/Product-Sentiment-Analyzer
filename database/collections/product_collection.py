from typing import Any, Dict, List, Optional
from pymongo.errors import DuplicateKeyError, PyMongoError
from database.config.database import DatabaseManager
from database.config.settings import Settings
from database.models.product import Product
from database.utils.logger import logger
from database.utils.validators import ValidationError, validate_product


class ProductCollection:
    """Encapsulates CRUD operations on the products collection."""

    def __init__(self):
        self.collection_name = Settings.PRODUCTS_COLLECTION

    def _get_coll(self):
        """Returns the PyMongo collection reference, or raises an exception if not connected."""
        coll = DatabaseManager.get_collection(self.collection_name)
        if coll is None:
            raise PyMongoError("Database connection is not established.")
        return coll

    def insert_product(self, product_data: Dict[str, Any]) -> bool:
        """Inserts a new product document. Validates the data before inserting."""
        try:
            # Validate input dictionary (will raise ValidationError if invalid)
            validate_product(product_data)

            # Ensure model to_dict is called (runs validation again and formats fields)
            product_obj = Product.from_dict(product_data)
            doc = product_obj.to_dict()

            coll = self._get_coll()
            coll.insert_one(doc)
            logger.info(f"Product inserted successfully: {product_obj.product_id}")
            return True
        except ValidationError as e:
            logger.error(f"Validation failed for product: {e}")
            raise
        except DuplicateKeyError as e:
            logger.error(f"Duplicate product_id error: {e}")
            raise ValueError(f"Product with ID '{product_data.get('product_id')}' already exists.") from e
        except PyMongoError as e:
            logger.error(f"Database error during product insert: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during product insert: {e}")
            raise

    def update_product(self, product_id: str, update_data: Dict[str, Any]) -> bool:
        """Updates an existing product's fields. Validates non-empty fields if provided."""
        try:
            coll = self._get_coll()
            # Perform a partial validation or full validation check on updated fields if needed.
            # We can check if fields exist in Product fields.
            if "product_id" in update_data and update_data["product_id"] != product_id:
                raise ValidationError("Changing product_id is not allowed.")

            # Validate pricing, rating, etc. if they are part of the update
            if "rating" in update_data:
                rating = update_data["rating"]
                if not isinstance(rating, (int, float)) or not (0.0 <= rating <= 5.0):
                    raise ValidationError(f"rating must be numeric and between 0.0 and 5.0, got: {rating}")
            if "price" in update_data:
                price = update_data["price"]
                if not isinstance(price, (int, float)) or price < 0:
                    raise ValidationError(f"price must be a non-negative number, got: {price}")
            if "discount_price" in update_data and update_data["discount_price"] is not None:
                disc = update_data["discount_price"]
                if not isinstance(disc, (int, float)) or disc < 0:
                    raise ValidationError(f"discount_price must be a non-negative number, got: {disc}")

            # Keep updated_at fresh
            update_data["updated_at"] = update_data.get("updated_at") or datetime.utcnow()

            result = coll.update_one({"product_id": product_id}, {"$set": update_data})
            if result.matched_count > 0:
                logger.info(f"Product updated: {product_id}")
                return True
            logger.warning(f"Product not found for update: {product_id}")
            return False
        except ValidationError as e:
            logger.error(f"Validation failed during update for product {product_id}: {e}")
            raise
        except PyMongoError as e:
            logger.error(f"Database error during product update {product_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during product update {product_id}: {e}")
            raise

    def delete_product(self, product_id: str) -> bool:
        """Deletes a product by product_id."""
        try:
            coll = self._get_coll()
            result = coll.delete_one({"product_id": product_id})
            if result.deleted_count > 0:
                logger.info(f"Product deleted: {product_id}")
                return True
            logger.warning(f"Product not found for deletion: {product_id}")
            return False
        except PyMongoError as e:
            logger.error(f"Database error during product deletion {product_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during product deletion {product_id}: {e}")
            raise

    def find_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Finds a single product by product_id."""
        try:
            coll = self._get_coll()
            doc = coll.find_one({"product_id": product_id})
            return doc
        except PyMongoError as e:
            logger.error(f"Database error during product find {product_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during product find {product_id}: {e}")
            raise

    def get_all_products(self, limit: int = 100, skip: int = 0) -> List[Dict[str, Any]]:
        """Retrieves list of all products with pagination support."""
        try:
            coll = self._get_coll()
            cursor = coll.find().skip(skip).limit(limit)
            return list(cursor)
        except PyMongoError as e:
            logger.error(f"Database error during get_all_products: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during get_all_products: {e}")
            raise


# Helper datetime import inside file to avoid global namespace pollution
from datetime import datetime
