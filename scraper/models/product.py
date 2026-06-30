"""
product.py – Product data model.

Defines the canonical structure for a scraped product.  The ``Product``
dataclass maps directly to the MongoDB document schema consumed by the
backend team.

Usage::

    from models.product import Product
    p = Product(product_id="B0CH7RLKFC", product_name="Sony WH-1000XM5", ...)
    doc = p.to_dict()   # MongoDB-ready dict
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class Product:
    """Represents a single scraped product.

    Attributes:
        product_id:       Unique identifier extracted from the URL
                          (e.g. Amazon ASIN, Flipkart PID).
        product_name:     Full product title.
        brand:            Manufacturer / brand name.
        category:         Product category or breadcrumb.
        price:            Listed price (original, in INR).
        discount_price:   Current selling / discounted price (in INR).
        overall_rating:   Aggregate star rating (0.0 – 5.0).
        num_ratings:      Total count of customer ratings.
        num_reviews:      Total count of written reviews.
        description:      Product description / feature bullet points.
        availability:     Stock status (e.g. 'In Stock', 'Out of Stock').
        image_url:        URL of the primary product image.
        product_url:      Full URL of the product page.
        source:           Platform identifier ('amazon' or 'flipkart').
        scraped_at:       ISO 8601 UTC timestamp of when the data was
                          collected.
    """

    product_id: str
    product_name: str
    brand: str | None = None
    category: str | None = None
    price: float | None = None
    discount_price: float | None = None
    overall_rating: float | None = None
    num_ratings: int | None = None
    num_reviews: int | None = None
    description: str | None = None
    availability: str | None = None
    image_url: str | None = None
    product_url: str | None = None
    source: str | None = None
    scraped_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Return a MongoDB-ready dictionary representation.

        All ``None`` fields are preserved so the backend always receives
        a predictable document structure.

        Returns:
            Dict mapping field names to values.
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Product":
        """Construct a :class:`Product` from a raw dictionary.

        Unknown keys are silently ignored to allow forward compatibility.

        Args:
            data: Dictionary (e.g. loaded from JSON).

        Returns:
            :class:`Product` instance.
        """
        known_fields = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        filtered = {k: v for k, v in data.items() if k in known_fields}
        return cls(**filtered)

    def __repr__(self) -> str:
        return (
            f"Product(id={self.product_id!r}, name={self.product_name!r}, "
            f"source={self.source!r})"
        )
