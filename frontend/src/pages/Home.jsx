import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { healthCheck } from "../services/api";

function Home() {
  const [apiStatus, setApiStatus] = useState("checking");

  useEffect(() => {
    healthCheck()
      .then((response) => {
        if (response.data && response.data.status === "ok") {
          setApiStatus("online");
        } else {
          setApiStatus("offline");
        }
      })
      .catch(() => setApiStatus("offline"));
  }, []);

  return (
    <section className="page-section">
      <div className="hero-layout">
        <div className="hero-text-content">
          <p className="eyebrow">Review Intelligence Platform</p>
          <h1>Analyze product reviews with sentiment-driven dashboards.</h1>
          <p className="hero-copy">
            Search any product across Amazon or Flipkart, automatically scrape customer reviews, 
            classify sentiment polarity, and view aggregated metrics inside our comprehensive visual dashboard.
          </p>
          <div className="action-row">
            <Link className="primary-button" to="/search">
              Start Search
            </Link>
            <Link className="secondary-button" to="/dashboard">
              View Dashboard
            </Link>
          </div>
        </div>
        <aside className="status-panel">
          <h3>System Integration</h3>
          <div className="status-indicator-row">
            <span>Backend API Status:</span>
            <strong className={`status-pill status-${apiStatus}`}>{apiStatus}</strong>
          </div>
          <p className="status-description">
            This health check communicates with the Flask backend. When offline, mock fallback data is automatically utilized.
          </p>
        </aside>
      </div>
    </section>
  );
}

export default Home;
