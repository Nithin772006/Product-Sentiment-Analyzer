import json
from pathlib import Path
from typing import Dict, List
from database.config.settings import Settings
from database.services.database_service import DatabaseService
from database.utils.logger import logger
from database.utils.helper import MongoJSONEncoder, parse_date


class BackupService:
    """Manages exporting database collections to JSON backups and restoring them back."""

    def __init__(self, db_service: DatabaseService, backup_dir: Optional[Path] = None):
        self.db_service = db_service
        # Default backup directory is database/backups/
        base_dir = Path(__file__).resolve().parent.parent
        self.backup_dir = backup_dir or (base_dir / "backups")
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def backup_database(self) -> Dict[str, str]:
        """Backs up products, reviews, and sentiments collections to JSON files in the backup directory."""
        results = {}
        try:
            logger.info(f"Starting Database Backup to directory: {self.backup_dir}")

            # Export Products
            products = self.db_service.get_all_products(limit=10000)
            prod_file = self.backup_dir / f"{Settings.PRODUCTS_COLLECTION}.json"
            with open(prod_file, "w", encoding="utf-8") as f:
                json.dump(products, f, cls=MongoJSONEncoder, indent=2)
            results["products"] = str(prod_file)

            # Export Reviews
            # Since get_product_reviews requires a product_id, let's query all from the PyMongo collection directly
            rev_coll = self.db_service.reviews._get_coll()
            reviews = list(rev_coll.find({}))
            rev_file = self.backup_dir / f"{Settings.REVIEWS_COLLECTION}.json"
            with open(rev_file, "w", encoding="utf-8") as f:
                json.dump(reviews, f, cls=MongoJSONEncoder, indent=2)
            results["reviews"] = str(rev_file)

            # Export Sentiments
            sent_coll = self.db_service.sentiments._get_coll()
            sentiments = list(sent_coll.find({}))
            sent_file = self.backup_dir / f"{Settings.SENTIMENTS_COLLECTION}.json"
            with open(sent_file, "w", encoding="utf-8") as f:
                json.dump(sentiments, f, cls=MongoJSONEncoder, indent=2)
            results["sentiments"] = str(sent_file)

            logger.info("Backup Completed successfully.")
            return results
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            raise

    def restore_database(self) -> bool:
        """Restores products, reviews, and sentiments from JSON files in the backup directory."""
        try:
            logger.info(f"Starting Database Restore from directory: {self.backup_dir}")

            # Clear DB collections first to ensure clean slate
            # We can use the same clean structure
            prod_coll = self.db_service.products._get_coll()
            rev_coll = self.db_service.reviews._get_coll()
            sent_coll = self.db_service.sentiments._get_coll()

            # 1. Restore Products
            prod_file = self.backup_dir / f"{Settings.PRODUCTS_COLLECTION}.json"
            if prod_file.exists():
                logger.info("Restoring products...")
                with open(prod_file, "r", encoding="utf-8") as f:
                    products = json.load(f)
                
                # Drop existing
                prod_coll.delete_many({})
                
                for prod in products:
                    # Strip mongodb internals like _id to avoid object ID conflicts if inserting clean
                    # Convert dates from ISO-8601 strings back to datetime objects
                    prod.pop("_id", None)
                    if "created_at" in prod:
                        prod["created_at"] = parse_date(prod["created_at"])
                    if "updated_at" in prod:
                        prod["updated_at"] = parse_date(prod["updated_at"])
                    self.db_service.insert_product(prod)
            else:
                logger.warning(f"Product backup file not found: {prod_file}")

            # 2. Restore Reviews
            rev_file = self.backup_dir / f"{Settings.REVIEWS_COLLECTION}.json"
            if rev_file.exists():
                logger.info("Restoring reviews...")
                with open(rev_file, "r", encoding="utf-8") as f:
                    reviews = json.load(f)
                
                # Drop existing
                rev_coll.delete_many({})

                for rev in reviews:
                    rev.pop("_id", None)
                    if "review_date" in rev:
                        rev["review_date"] = parse_date(rev["review_date"])
                    if "created_at" in rev:
                        rev["created_at"] = parse_date(rev["created_at"])
                    self.db_service.insert_review(rev)
            else:
                logger.warning(f"Review backup file not found: {rev_file}")

            # 3. Restore Sentiments
            sent_file = self.backup_dir / f"{Settings.SENTIMENTS_COLLECTION}.json"
            if sent_file.exists():
                logger.info("Restoring sentiments...")
                with open(sent_file, "r", encoding="utf-8") as f:
                    sentiments = json.load(f)

                # Drop existing
                sent_coll.delete_many({})

                for sent in sentiments:
                    sent.pop("_id", None)
                    if "analyzed_at" in sent:
                        sent["analyzed_at"] = parse_date(sent["analyzed_at"])
                    self.db_service.insert_sentiment(sent)
            else:
                logger.warning(f"Sentiment backup file not found: {sent_file}")

            logger.info("Restore completed successfully.")
            return True
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            raise


from typing import Optional
