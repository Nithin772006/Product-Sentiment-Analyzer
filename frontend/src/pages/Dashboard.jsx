import { useEffect, useState } from "react";
import { Bar, Doughnut } from "react-chartjs-2";
import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  ArcElement,
  Legend,
  LinearScale,
  Tooltip,
} from "chart.js";

import { getDashboard } from "../api/productApi";
import StatCard from "../components/StatCard.jsx";


ChartJS.register(ArcElement, BarElement, CategoryScale, LinearScale, Legend, Tooltip);


function Dashboard() {
  const [dashboard, setDashboard] = useState(null);

  useEffect(() => {
    getDashboard()
      .then((response) => setDashboard(response.data))
      .catch(() => setDashboard(null));
  }, []);

  if (!dashboard) {
    return (
      <section className="page-section compact">
        <p className="loading-state">Loading dashboard data...</p>
      </section>
    );
  }

  const sentimentChart = {
    labels: ["Positive", "Neutral", "Negative"],
    datasets: [
      {
        data: [
          dashboard.sentimentDistribution.positive,
          dashboard.sentimentDistribution.neutral,
          dashboard.sentimentDistribution.negative,
        ],
        backgroundColor: ["#1f9d55", "#f2b705", "#d64545"],
      },
    ],
  };

  const ratingChart = {
    labels: Object.keys(dashboard.ratingDistribution),
    datasets: [
      {
        label: "Reviews",
        data: Object.values(dashboard.ratingDistribution),
        backgroundColor: "#315c8c",
      },
    ],
  };

  return (
    <section className="page-section compact">
      <div className="section-heading">
        <p className="eyebrow">Dashboard</p>
        <h1>Review sentiment overview.</h1>
      </div>

      <div className="stat-grid">
        <StatCard label="Total Reviews" value={dashboard.summary.totalReviews} />
        <StatCard label="Average Rating" value={dashboard.summary.averageRating} />
        <StatCard label="Positive" value={`${dashboard.summary.positivePercentage}%`} />
        <StatCard label="Negative" value={`${dashboard.summary.negativePercentage}%`} />
      </div>

      <div className="chart-grid">
        <article className="chart-panel">
          <h2>Sentiment Distribution</h2>
          <Doughnut data={sentimentChart} />
        </article>
        <article className="chart-panel">
          <h2>Rating Distribution</h2>
          <Bar data={ratingChart} />
        </article>
      </div>

      <div className="keyword-row">
        {dashboard.recentKeywords.map((keyword) => (
          <span key={keyword}>{keyword}</span>
        ))}
      </div>
    </section>
  );
}

export default Dashboard;
