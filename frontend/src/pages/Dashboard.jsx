import React, { useEffect, useState } from "react";

import { getDashboard, getProducts } from "../services/api";
import StatisticsCard from "../components/StatisticsCard.jsx";
import SentimentChart from "../components/SentimentChart.jsx";
import RatingChart from "../components/RatingChart.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import ErrorMessage from "../components/ErrorMessage.jsx";

function Dashboard() {
  const [dashboard, setDashboard] = useState(null);
  const [productsCount, setProductsCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboardData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [dashResponse, prodResponse] = await Promise.all([
        getDashboard(),
        getProducts(),
      ]);
      setDashboard(dashResponse.data);
      setProductsCount(prodResponse.data?.length || 0);
    } catch (err) {
      setError("Failed to connect to the backend dashboard API. Please ensure the Flask app is running.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  if (isLoading) {
    return <LoadingSpinner message="Generating sentiment charts and loading dashboard metrics..." />;
  }

  if (error) {
    return (
      <section className="page-section compact">
        <ErrorMessage message={error} onRetry={fetchDashboardData} />
      </section>
    );
  }

  if (!dashboard) {
    return (
      <section className="page-section compact">
        <p className="loading-state">No dashboard data found.</p>
      </section>
    );
  }

  const { summary, sentimentDistribution, ratingDistribution, recentKeywords } = dashboard;

  return (
    <section className="page-section dashboard-page-container">
      <div className="section-heading">
        <p className="eyebrow">Analytics Dashboard</p>
        <h1>Sentiment & Review Insights</h1>
        <p className="section-description">
          A high-level view of customer sentiment ratios, product rating distribution, and keyword frequencies extracted from crawled feedback.
        </p>
      </div>

      {/* Statistics Cards Grid */}
      <div className="stat-grid">
        <StatisticsCard
          title="Total Products"
          value={productsCount}
          icon="default"
          helperText="Active scraped items"
        />
        <StatisticsCard
          title="Total Reviews"
          value={summary.totalReviews}
          icon="reviews"
          helperText="Scraped from portals"
        />
        <StatisticsCard
          title="Average Rating"
          value={`${summary.averageRating} / 5`}
          icon="rating"
          helperText="Aggregated customer score"
        />
        <StatisticsCard
          title="Positive Reviews"
          value={`${sentimentDistribution.positive} (${summary.positivePercentage}%)`}
          icon="positive"
          helperText="Optimistic feedback"
        />
        <StatisticsCard
          title="Neutral Reviews"
          value={`${sentimentDistribution.neutral} (${summary.neutralPercentage}%)`}
          icon="neutral"
          helperText="Indifferent feedback"
        />
        <StatisticsCard
          title="Negative Reviews"
          value={`${sentimentDistribution.negative} (${summary.negativePercentage}%)`}
          icon="negative"
          helperText="Critical complaints"
        />
      </div>

      {/* Chart Visualization Grid */}
      <div className="chart-grid">
        <article className="chart-panel">
          <h2>Sentiment Distribution</h2>
          <SentimentChart sentimentDistribution={sentimentDistribution} />
        </article>
        <article className="chart-panel">
          <h2>Rating Distribution</h2>
          <RatingChart ratingDistribution={ratingDistribution} />
        </article>
      </div>

      {/* Keywords Cloud */}
      <div className="keywords-cloud-panel">
        <h2>Frequently Discussed Topics</h2>
        <div className="keyword-row">
          {recentKeywords.map((keyword) => (
            <span key={keyword} className="keyword-chip">
              #{keyword}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}

export default Dashboard;
