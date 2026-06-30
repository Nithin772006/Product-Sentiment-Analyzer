import React from "react";

function ErrorMessage({ message = "An unexpected error occurred.", onRetry, details }) {
  return (
    <div className="error-message-container" role="alert">
      <div className="error-card">
        <div className="error-icon-wrapper">
          <svg className="error-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <h3 className="error-title">Error</h3>
        <p className="error-message-text">{message}</p>
        {details && (
          <details className="error-details">
            <summary>More Info</summary>
            <pre>{details}</pre>
          </details>
        )}
        {onRetry && (
          <button onClick={onRetry} className="primary-button error-retry-button">
            Try Again
          </button>
        )}
      </div>
    </div>
  );
}

export default ErrorMessage;
