import React from "react";
import { Doughnut } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";

// Register ChartJS elements
ChartJS.register(ArcElement, Tooltip, Legend);

function SentimentChart({ sentimentDistribution }) {
  if (!sentimentDistribution) return <p className="no-data">No sentiment data available</p>;

  const { positive = 0, neutral = 0, negative = 0 } = sentimentDistribution;

  const data = {
    labels: ["Positive", "Neutral", "Negative"],
    datasets: [
      {
        data: [positive, neutral, negative],
        backgroundColor: [
          "rgba(22, 115, 71, 0.8)",  // Soft emerald green
          "rgba(242, 183, 5, 0.8)",  // Warm yellow
          "rgba(180, 35, 24, 0.8)",   // Muted red
        ],
        borderColor: [
          "rgba(22, 115, 71, 1)",
          "rgba(242, 183, 5, 1)",
          "rgba(180, 35, 24, 1)",
        ],
        borderWidth: 2,
        hoverOffset: 6,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "bottom",
        labels: {
          padding: 20,
          color: "#405064",
          font: {
            size: 12,
            weight: "600",
          },
        },
      },
      tooltip: {
        backgroundColor: "rgba(23, 32, 42, 0.9)",
        titleFont: { size: 13, weight: "bold" },
        bodyFont: { size: 12 },
        padding: 10,
        cornerRadius: 6,
        callbacks: {
          label: (context) => {
            const label = context.label || "";
            const value = context.raw || 0;
            const total = context.dataset.data.reduce((a, b) => a + b, 0);
            const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
            return ` ${label}: ${value} (${percentage}%)`;
          },
        },
      },
    },
    cutout: "70%",
  };

  return (
    <div className="chart-wrapper" style={{ height: "300px", position: "relative" }}>
      <Doughnut data={data} options={options} />
    </div>
  );
}

export default SentimentChart;
