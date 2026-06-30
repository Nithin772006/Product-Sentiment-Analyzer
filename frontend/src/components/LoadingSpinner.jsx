import React from "react";

function LoadingSpinner({ message = "Gathering review data and analyzing sentiment..." }) {
  return (
    <div className="loading-spinner-overlay" role="status" aria-live="polite">
      <div className="loading-spinner-container">
        <div className="spinner"></div>
        {message && <p className="loading-message">{message}</p>}
      </div>
    </div>
  );
}

export default LoadingSpinner;
