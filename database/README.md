# Database Module - MongoDB Atlas

This directory contains the MongoDB Atlas Database layer for the **Product Sentiment Analyzer and Review Dashboard** project.

## Database Architecture

The database module isolates MongoDB-specific code from rest of the application. It consists of configuration managers, dataclasses/models, collection-specific operations (repositories), high-level services, and administrative scripts.

```text
database/
├── config/
│   ├── database.py       # Client initialization & connection singleton
│   └── settings.py       # Configuration settings loader (environment variables)
├── collections/
│   ├── product_collection.py
│   ├── review_collection.py
│   └── sentiment_collection.py
├── models/
│   ├── product.py
│   ├── review.py
│   └── sentiment.py
├── services/
│   ├── database_service.py # Unified CRUD Service wrapper
│   ├── seed_service.py     # Populates mock data for local environments
│   └── backup_service.py   # Database backup and restore implementation
├── utils/
│   ├── logger.py         # Custom logs handler (writes to database/logs/database.log)
│   ├── validators.py     # Custom application validation rules
│   └── helper.py         # Type conversions and serializers
├── scripts/
│   ├── create_indexes.py # Schema indexing setup
│   ├── seed_database.py  # Run mock seeding command
│   └── backup_database.py# Export/Restore collections command
├── logs/                 # Active diagnostic logging folder
├── tests/                # Unit test suites
├── main.py               # Layer entry point & diagnostic checker
└── requirements.txt      # Dependency specification
```

---

## Connection Setup

Configuration is loaded from environment variables in `database/.env`. Do not hardcode credentials.

Copy `.env.example` to `.env` and configure your credentials:
```env
MONGO_URI=mongodb+srv://<username>:<password>@<cluster-url>/product_sentiment_db
DATABASE_NAME=product_sentiment_db
```

---

## Database Schemas & Collection Fields

### 1. Products Collection (`products`)
* `product_id` (String, Unique Index, Required): Identifier of the product.
* `product_name` (String, Required): Display name of the product.
* `brand` (String, Required): Product manufacturer.
* `category` (String, Required): Category taxonomy.
* `description` (String): Product specification summary.
* `price` (Float, Required): Normal retail price.
* `discount_price` (Float/None): Lowered price (if running promotions).
* `rating` (Float, Required): Aggregated stars (0.0 to 5.0).
* `total_reviews` (Int): Total scraped reviews.
* `availability` (Boolean): Current stock status.
* `image_url` (String): Remote path to item photo.
* `product_url` (String): Direct link to retail marketplace page.
* `created_at` (Datetime): Insertion timestamp.
* `updated_at` (Datetime): Update timestamp.

### 2. Reviews Collection (`reviews`)
* `review_id` (String, Unique Index, Required): Identifier of the review.
* `product_id` (String, Required): Associated product identifier.
* `reviewer_name` (String, Required): Review author.
* `review_title` (String): Review summary header.
* `review_text` (String, Required): Raw body content.
* `rating` (Float, Required): Stars given by reviewer (0.0 to 5.0).
* `verified_purchase` (Boolean): Purchase verification flag.
* `review_date` (Datetime): Original publish date.
* `helpful_votes` (Int): Helpful counts.
* `sentiment` (String): Extracted polarity label (`positive`, `neutral`, `negative`).
* `confidence_score` (Float): AI labeling probability confidence.
* `created_at` (Datetime): Database record creation.

### 3. Sentiments Collection (`sentiments`)
* `review_id` (String, Unique Index, Required): Link to review document.
* `sentiment` (String, Required): Polarity category (`positive`, `neutral`, `negative`).
* `positive_score` (Float, Required): Confidence of positive features (0.0 to 1.0).
* `neutral_score` (Float, Required): Confidence of neutral features (0.0 to 1.0).
* `negative_score` (Float, Required): Confidence of negative features (0.0 to 1.0).
* `compound_score` (Float, Required): Normalized score (-1.0 to 1.0).
* `confidence_score` (Float, Required): VADER/BERT classifier accuracy probability.
* `analyzed_at` (Datetime): Time sentiment analysis was run.

---

## Validation Rules

Documents are verified both at the Python application level (raising `ValidationError`) and can also check for schema formats:
1. **Required Fields**: Throws exceptions if fields missing.
2. **Numeric Ratings**: Rating must be between `0.0` and `5.0`.
3. **Price format**: Prices must be positive floats; `discount_price` must not exceed normal `price`.
4. **Sentiment values**: Must match one of `positive`, `neutral`, or `negative`.
5. **Date formats**: Ensures proper datetimes or ISO-8601 formatting.

---

## Indexing

Run the script to build database search indexes:
```bash
python scripts/create_indexes.py
```
This sets up:
* Unique index on `product_id`, `review_id`.
* ASCENDING indexes on `brand`, `category`, `product_id`, `sentiment`.
* DESCENDING sorting index on `rating`.
* TEXT indexing on `product_name` for full-text search capability.

---

## CRUD Operations

The `DatabaseService` class is the central CRUD interface:

```python
from services.database_service import DatabaseService

db_service = DatabaseService()

# Find a product
product = db_service.find_product("prod_001")

# Insert review
db_service.insert_review({
    "review_id": "rev_200",
    "product_id": "prod_001",
    "reviewer_name": "Dave",
    "review_text": "Pretty good product.",
    "rating": 4.0
})
```

---

## Backup & Restore

Backup the database collections to JSON files:
```bash
python scripts/backup_database.py --action backup
```
Restore documents back from backup JSON files:
```bash
python scripts/backup_database.py --action restore
```
By default, files are exported to `database/backups/`. You can specify a custom backup folder using the `--dir` option:
```bash
python scripts/backup_database.py --action backup --dir /path/to/backup_folder
```

---

## Testing

Run database unit tests:
```bash
python -m unittest discover -s tests
```
This tests connectivity, validators, model conversion, and CRUD mock workflows.
