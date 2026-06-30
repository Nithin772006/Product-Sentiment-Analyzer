import React from "react";

function ProductCard({ product, onClick }) {
  if (!product) return null;

  const { name, brand, price, rating, reviewCount, image } = product;

  // Star visual representation
  const renderStars = (ratingVal) => {
    const stars = [];
    const floorRating = Math.floor(ratingVal);
    for (let i = 1; i <= 5; i++) {
      if (i <= floorRating) {
        stars.push(<span key={i} className="star filled">★</span>);
      } else if (i - 0.5 <= ratingVal) {
        stars.push(<span key={i} className="star half">★</span>);
      } else {
        stars.push(<span key={i} className="star empty">★</span>);
      }
    }
    return stars;
  };

  return (
    <article className="product-card" onClick={onClick} style={{ cursor: onClick ? "pointer" : "default" }}>
      {image && (
        <div className="product-card-image-container">
          <img src={image} alt={name} className="product-card-image" />
        </div>
      )}
      <div className="product-card-content">
        <div className="product-brand-price">
          <span className="product-brand">{brand}</span>
          <span className="product-price">{price}</span>
        </div>
        <h3 className="product-name">{name}</h3>
        <div className="product-rating-container">
          <div className="stars-wrapper">{renderStars(rating)}</div>
          <span className="rating-value">{rating}</span>
          <span className="review-count">({reviewCount} reviews)</span>
        </div>
      </div>
    </article>
  );
}

export default ProductCard;
