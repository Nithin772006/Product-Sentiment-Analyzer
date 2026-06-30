import argparse
import sys
from pathlib import Path

# Add database package to python path
db_path = Path(__file__).resolve().parent.parent
sys.path.append(str(db_path))
sys.path.append(str(db_path.parent))

from database.services.database_service import DatabaseService
from database.services.backup_service import BackupService
from database.utils.logger import logger


def main():
    """Main CLI handler for backup and restore scripts."""
    parser = argparse.ArgumentParser(description="Backup and Restore utilities for MongoDB Atlas collections.")
    parser.add_argument(
        "--action",
        choices=["backup", "restore"],
        required=True,
        help="Select 'backup' to export collections to JSON, or 'restore' to import them back."
    )
    parser.add_argument(
        "--dir",
        type=str,
        default=None,
        help="Optional custom backup directory path."
    )

    args = parser.parse_args()
    backup_path = Path(args.dir) if args.dir else None

    try:
        db_service = DatabaseService()
        backup_service = BackupService(db_service, backup_dir=backup_path)

        if args.action == "backup":
            logger.info("Executing database backup command...")
            results = backup_service.backup_database()
            logger.info(f"Database backup files saved: {results}")
            print(f"Backup Completed successfully. Files: {results}")
        elif args.action == "restore":
            logger.info("Executing database restore command...")
            success = backup_service.restore_database()
            if success:
                logger.info("Database restore command completed successfully.")
                print("Restore completed successfully.")
            else:
                logger.error("Database restore command failed.")
                sys.exit(1)
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Backup/Restore action failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
