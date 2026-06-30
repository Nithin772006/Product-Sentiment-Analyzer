import React from "react";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from "chart.js";

// Register components locally to ensure encapsulation
ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

function RatingChart({ ratingDistribution }) {
  if (!ratingDistribution) return <p className="no-data">No rating data available</p>;

  // Sort keys to ensure stars display from 1 to 5
  const sortedKeys = Object.keys(ratingDistribution).sort((a, b) => Number(a) - Number(b));
  const dataValues = sortedKeys.map((key) => ratingDistribution[key]);

  const data = {
    labels: sortedKeys.map((key) => `${key} Star${Number(key) > 1 ? "s" : ""}`),
    datasets: [
      {
        label: "Number of Reviews",
        data: dataValues,
        backgroundColor: "rgba(15, 98, 168, 0.75)",
        borderColor: "rgba(15, 98, 168, 1)",
        borderWidth: 1.5,
        borderRadius: 6,
        hoverBackgroundColor: "rgba(15, 98, 168, 0.95)",
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: "rgba(23, 32, 42, 0.9)",
        titleFont: { size: 13, weight: "bold" },
        bodyFont: { size: 12 },
        padding: 10,
        cornerRadius: 6,
      },
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
        ticks: {
          color: "#405064",
          font: { weight: "600" },
        },
      },
      y: {
        grid: {
          color: "rgba(216, 222, 232, 0.5)",
        },
        ticks: {
          color: "#405064",
          stepSize: 1,
        },
      },
    },
  };

  return (
    <div className="chart-wrapper" style={{ height: "300px", position: "relative" }}>
      <Bar data={data} options={options} />
    </div>
  );
}

export default RatingChart;
