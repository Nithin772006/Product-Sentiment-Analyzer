import sys
from pathlib import Path

# Add database package to python path
db_path = Path(__file__).resolve().parent.parent
sys.path.append(str(db_path))
sys.path.append(str(db_path.parent))

from database.services.database_service import DatabaseService
from database.services.seed_service import SeedService
from database.utils.logger import logger


def main():
    """Main entrypoint script to execute database seeding."""
    try:
        db_service = DatabaseService()
        seed_service = SeedService(db_service)
        logger.info("Starting seed database process...")
        success = seed_service.seed_database()
        if success:
            logger.info("Database seeding finished successfully.")
            sys.exit(0)
        else:
            logger.error("Database seeding finished with errors.")
            sys.exit(1)
    except Exception as e:
        logger.critical(f"Unhandled exception during database seeding: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
