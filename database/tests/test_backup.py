import json
import shutil
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add root database directory to python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from services.backup_service import BackupService
from services.database_service import DatabaseService


class TestBackupService(unittest.TestCase):
    """Tests the Database backup and restore service utilities."""

    def setUp(self):
        # Create a temporary directory for backups during testing
        self.test_dir = Path(__file__).resolve().parent / "temp_backups"
        self.test_dir.mkdir(parents=True, exist_ok=True)
        
        # Mock database service
        self.mock_db = MagicMock(spec=DatabaseService)
        self.backup_service = BackupService(self.mock_db, backup_dir=self.test_dir)

    def tearDown(self):
        # Clean up temporary test files
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_backup_database_success(self):
        """Should dump records to JSON files in the backup folder."""
        # Setup mock returns
        self.mock_db.get_all_products.return_value = [{"product_id": "p1", "price": 10.0}]
        
        mock_rev_coll = MagicMock()
        mock_rev_coll.find.return_value = [{"review_id": "r1", "rating": 5.0}]
        self.mock_db.reviews._get_coll.return_value = mock_rev_coll

        mock_sent_coll = MagicMock()
        mock_sent_coll.find.return_value = [{"review_id": "r1", "sentiment": "positive"}]
        self.mock_db.sentiments._get_coll.return_value = mock_sent_coll

        # Run backup
        results = self.backup_service.backup_database()
        
        # Verify files were generated
        self.assertIn("products", results)
        self.assertIn("reviews", results)
        self.assertIn("sentiments", results)
        
        self.assertTrue(Path(results["products"]).exists())
        self.assertTrue(Path(results["reviews"]).exists())
        self.assertTrue(Path(results["sentiments"]).exists())

        # Verify content
        with open(results["products"], "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(data[0]["product_id"], "p1")

    def test_restore_database_success(self):
        """Should read files from the backup folder, drop collections, and run inserts."""
        # Create fake backup files
        prod_data = [{"product_id": "p1", "price": 10.0}]
        rev_data = [{"review_id": "r1", "rating": 5.0}]
        sent_data = [{"review_id": "r1", "sentiment": "positive"}]

        with open(self.test_dir / "products.json", "w", encoding="utf-8") as f:
            json.dump(prod_data, f)
        with open(self.test_dir / "reviews.json", "w", encoding="utf-8") as f:
            json.dump(rev_data, f)
        with open(self.test_dir / "sentiments.json", "w", encoding="utf-8") as f:
            json.dump(sent_data, f)

        # Mock collection drops
        mock_prod_coll = MagicMock()
        self.mock_db.products._get_coll.return_value = mock_prod_coll

        mock_rev_coll = MagicMock()
        self.mock_db.reviews._get_coll.return_value = mock_rev_coll

        mock_sent_coll = MagicMock()
        self.mock_db.sentiments._get_coll.return_value = mock_sent_coll

        # Run restore
        success = self.backup_service.restore_database()
        self.assertTrue(success)

        # Verify drops and inserts were called
        mock_prod_coll.delete_many.assert_called_with({})
        mock_rev_coll.delete_many.assert_called_with({})
        mock_sent_coll.delete_many.assert_called_with({})

        self.mock_db.insert_product.assert_called()
        self.mock_db.insert_review.assert_called()
        self.mock_db.insert_sentiment.assert_called()


if __name__ == "__main__":
    unittest.main()
