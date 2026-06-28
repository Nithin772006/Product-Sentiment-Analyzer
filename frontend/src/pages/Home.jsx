import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { checkApiHealth } from "../api/productApi";


function Home() {
  const [apiStatus, setApiStatus] = useState("checking");

  useEffect(() => {
    checkApiHealth()
      .then((response) => setApiStatus(response.data.status))
      .catch(() => setApiStatus("offline"));
  }, []);

  return (
    <section className="page-section">
      <div className="hero-layout">
        <div>
          <p className="eyebrow">Review Intelligence Platform</p>
          <h1>Analyze product reviews with sentiment-driven dashboards.</h1>
          <p className="hero-copy">
            Search a product, collect review data, classify customer sentiment,
            and convert feedback into clear dashboard insights.
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
          <span>Backend API</span>
          <strong className={`status-pill status-${apiStatus}`}>{apiStatus}</strong>
          <p>
            The health check uses the Flask endpoint and helps verify local
            development setup.
          </p>
        </aside>
      </div>
    </section>
  );
}

export default Home;
