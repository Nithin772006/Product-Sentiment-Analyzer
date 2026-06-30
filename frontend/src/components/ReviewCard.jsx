import React from "react";

function ReviewCard({ review }) {
  if (!review) return null;

  const { reviewerName = "Anonymous", title, reviewText, rating, sentiment, sentimentScore, date = "N/A" } = review;

  const renderStars = (ratingVal) => {
    const stars = [];
    for (let i = 1; i <= 5; i++) {
      stars.push(
        <span key={i} className={`star ${i <= rating ? "filled" : "empty"}`}>
          ★
        </span>
      );
    }
    return stars;
  };

  const getSentimentClass = (sentimentVal) => {
    const s = sentimentVal?.toLowerCase() || "";
    if (s === "positive") return "sentiment-badge-positive";
    if (s === "negative") return "sentiment-badge-negative";
    return "sentiment-badge-neutral";
  };

  return (
    <article className="review-card">
      <div className="review-card-header">
        <div className="reviewer-info">
          <strong className="reviewer-name">{reviewerName}</strong>
          <span className="review-date">{date}</span>
        </div>
        <div className={`sentiment-badge ${getSentimentClass(sentiment)}`}>
          {sentiment} {sentimentScore !== undefined && `(${(sentimentScore * 100).toFixed(0)}%)`}
        </div>
      </div>
      <div className="review-rating-row">
        <div className="stars-wrapper">{renderStars(rating)}</div>
        {title && <h4 className="review-title">{title}</h4>}
      </div>
      <p className="review-text">{reviewText}</p>
    </article>
  );
}

export default ReviewCard;
