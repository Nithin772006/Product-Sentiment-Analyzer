from datetime import datetime
from typing import Any, Dict, Optional
from database.utils.validators import validate_product
from database.utils.helper import parse_date


class Product:
    """Represents a Product document schema and helper methods."""

    def __init__(
        self,
        product_id: str,
        product_name: str,
        brand: str,
        category: str,
        price: float,
        rating: float,
        description: Optional[str] = "",
        discount_price: Optional[float] = None,
        total_reviews: Optional[int] = 0,
        availability: Optional[bool] = True,
        image_url: Optional[str] = "",
        product_url: Optional[str] = "",
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.product_id = product_id
        self.product_name = product_name
        self.brand = brand
        self.category = category
        self.description = description
        self.price = float(price)
        self.discount_price = float(discount_price) if discount_price is not None else None
        self.rating = float(rating)
        self.total_reviews = int(total_reviews) if total_reviews is not None else 0
        self.availability = bool(availability)
        self.image_url = image_url
        self.product_url = product_url
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Converts the Product object into a dictionary for MongoDB insertion."""
        doc = {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "brand": self.brand,
            "category": self.category,
            "description": self.description,
            "price": self.price,
            "discount_price": self.discount_price,
            "rating": self.rating,
            "total_reviews": self.total_reviews,
            "availability": self.availability,
            "image_url": self.image_url,
            "product_url": self.product_url,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        # Run validation before returning dict
        validate_product(doc)
        return doc

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Product":
        """Creates a Product object from a dictionary."""
        # Ensure validation is run
        validate_product(data)

        return cls(
            product_id=data["product_id"],
            product_name=data["product_name"],
            brand=data["brand"],
            category=data["category"],
            description=data.get("description", ""),
            price=data["price"],
            discount_price=data.get("discount_price"),
            rating=data["rating"],
            total_reviews=data.get("total_reviews", 0),
            availability=data.get("availability", True),
            image_url=data.get("image_url", ""),
            product_url=data.get("product_url", ""),
            created_at=parse_date(data.get("created_at")),
            updated_at=parse_date(data.get("updated_at")),
        )
