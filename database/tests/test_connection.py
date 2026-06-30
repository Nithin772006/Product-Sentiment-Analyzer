import sys
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

# Add root database directory to python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from config.database import DatabaseManager
from scripts.create_indexes import create_all_indexes
from pymongo.errors import ConnectionFailure


class TestConnectionAndIndexes(unittest.TestCase):
    """Tests connection setup and index building utilities."""

    @patch("config.database.MongoClient")
    def test_database_manager_connection_success(self, mock_mongo_client):
        """Should connect successfully when ping succeeds."""
        # Reset singleton to force re-evaluation
        DatabaseManager._client = None
        
        # Configure client mock
        mock_client_instance = mock_mongo_client.return_value
        mock_client_instance.admin.command.return_value = {"ok": 1.0}
        
        client = DatabaseManager.get_client()
        self.assertIsNotNone(client)
        mock_client_instance.admin.command.assert_called_with("ping")

    @patch("config.database.MongoClient")
    def test_database_manager_connection_failure(self, mock_mongo_client):
        """Should log failure and return None on connection ping error."""
        DatabaseManager._client = None
        
        mock_mongo_client.side_effect = ConnectionFailure("Could not connect")
        
        client = DatabaseManager.get_client()
        self.assertNone(client)

    @patch("config.database.DatabaseManager.get_collection")
    def test_create_indexes(self, mock_get_collection):
        """Should create ASCENDING, DESCENDING, and TEXT indexes on correct collections."""
        mock_prod = MagicMock()
        mock_rev = MagicMock()
        mock_sent = MagicMock()
        
        def side_effect(coll_name):
            if coll_name == "products":
                return mock_prod
            elif coll_name == "reviews":
                return mock_rev
            elif coll_name == "sentiments":
                return mock_sent
            return None
            
        mock_get_collection.side_effect = side_effect
        
        success = create_all_indexes()
        self.assertTrue(success)
        
        # Verify index creation methods called
        mock_prod.create_index.assert_called()
        mock_rev.create_index.assert_called()
        mock_sent.create_index.assert_called()


if __name__ == "__main__":
    unittest.main()
