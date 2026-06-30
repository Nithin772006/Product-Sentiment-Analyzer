import React from "react";

function StatisticsCard({ title, value, icon, helperText }) {
  // Renders a fallback SVG icon depending on the icon name
  const renderIcon = (iconName) => {
    switch (iconName) {
      case "reviews":
        return (
          <svg className="stat-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        );
      case "rating":
        return (
          <svg className="stat-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.907c.961 0 1.36 1.252.587 1.813l-3.974 2.89a1 1 0 00-.364 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.88a1 1 0 00-1.176 0l-3.976 2.88c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.364-1.118L2.05 10.104c-.773-.562-.373-1.813.587-1.813h4.906a1 1 0 00.95-.69l1.52-4.674z" />
          </svg>
        );
      case "positive":
        return (
          <svg className="stat-icon text-positive" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      case "negative":
        return (
          <svg className="stat-icon text-negative" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      case "neutral":
        return (
          <svg className="stat-icon text-neutral" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-8 4h8" />
          </svg>
        );
      default:
        return (
          <svg className="stat-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
    }
  };

  return (
    <article className="stat-card statistics-card">
      <div className="stat-header">
        <span className="stat-label">{title}</span>
        {icon && <span className="stat-icon-wrapper">{renderIcon(icon)}</span>}
      </div>
      <div className="stat-body">
        <strong className="stat-value">{value}</strong>
        {helperText && <span className="stat-helper">{helperText}</span>}
      </div>
    </article>
  );
}

export default StatisticsCard;
