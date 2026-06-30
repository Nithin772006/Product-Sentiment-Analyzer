import sys
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

# Add root database directory to python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from services.database_service import DatabaseService
from pymongo.errors import DuplicateKeyError


class TestCRUDOperations(unittest.TestCase):
    """Tests all CRUD operations on DatabaseService using mocked collections."""

    def setUp(self):
        # Patch DatabaseManager.get_collection globally for these tests
        self.patcher = patch("config.database.DatabaseManager.get_collection")
        self.mock_get_collection = self.patcher.start()
        
        # Create mock collections
        self.mock_prod_coll = MagicMock()
        self.mock_rev_coll = MagicMock()
        self.mock_sent_coll = MagicMock()
        
        # Configure get_collection to return the correct mock based on argument
        def side_effect(coll_name):
            if coll_name == "products":
                return self.mock_prod_coll
            elif coll_name == "reviews":
                return self.mock_rev_coll
            elif coll_name == "sentiments":
                return self.mock_sent_coll
            return MagicMock()

        self.mock_get_collection.side_effect = side_effect
        
        # Instantiate service to test
        self.db_service = DatabaseService()

    def tearDown(self):
        self.patcher.stop()

    def test_insert_product_success(self):
        """Should insert product successfully and return True."""
        product_data = {
            "product_id": "prod_1",
            "product_name": "Chair",
            "brand": "BrandA",
            "category": "Furniture",
            "price": 49.99,
            "rating": 4.0,
        }
        self.mock_prod_coll.insert_one.return_value = MagicMock(acknowledged=True)
        
        result = self.db_service.insert_product(product_data)
        self.assertTrue(result)
        self.mock_prod_coll.insert_one.assert_called_once()

    def test_insert_product_duplicate_key(self):
        """Should raise ValueError on duplicate product insertion."""
        product_data = {
            "product_id": "prod_1",
            "product_name": "Chair",
            "brand": "BrandA",
            "category": "Furniture",
            "price": 49.99,
            "rating": 4.0,
        }
        self.mock_prod_coll.insert_one.side_effect = DuplicateKeyError("Duplicate key")
        
        with self.assertRaises(ValueError):
            self.db_service.insert_product(product_data)

    def test_find_product(self):
        """Should query product details correctly."""
        dummy_product = {
            "product_id": "prod_1",
            "product_name": "Chair",
            "brand": "BrandA",
            "category": "Furniture",
            "price": 49.99,
            "rating": 4.0,
        }
        self.mock_prod_coll.find_one.return_value = dummy_product
        
        result = self.db_service.find_product("prod_1")
        self.assertEqual(result["product_name"], "Chair")
        self.mock_prod_coll.find_one.assert_called_with({"product_id": "prod_1"})

    def test_update_product(self):
        """Should update product attributes successfully."""
        self.mock_prod_coll.update_one.return_value = MagicMock(matched_count=1)
        
        result = self.db_service.update_product("prod_1", {"price": 39.99})
        self.assertTrue(result)
        self.mock_prod_coll.update_one.assert_called_once()

    def test_delete_product(self):
        """Should remove product record successfully."""
        self.mock_prod_coll.delete_one.return_value = MagicMock(deleted_count=1)
        
        result = self.db_service.delete_product("prod_1")
        self.assertTrue(result)
        self.mock_prod_coll.delete_one.assert_called_with({"product_id": "prod_1"})

    def test_insert_review_success(self):
        """Should insert review record successfully."""
        review_data = {
            "review_id": "rev_1",
            "product_id": "prod_1",
            "reviewer_name": "Dave",
            "review_text": "Average.",
            "rating": 3.0,
        }
        self.mock_rev_coll.insert_one.return_value = MagicMock(acknowledged=True)
        
        result = self.db_service.insert_review(review_data)
        self.assertTrue(result)
        self.mock_rev_coll.insert_one.assert_called_once()


if __name__ == "__main__":
    unittest.main()
