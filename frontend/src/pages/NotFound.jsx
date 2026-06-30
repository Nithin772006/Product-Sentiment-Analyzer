import React from "react";
import { Link } from "react-router-dom";

function NotFound() {
  return (
    <section className="page-section compact not-found-section" style={{ textAlign: "center", padding: "100px 20px" }}>
      <div className="not-found-card">
        <h1 className="error-code" style={{ fontSize: "6rem", margin: 0, color: "#0f62a8" }}>404</h1>
        <h2 style={{ fontSize: "2rem", margin: "10px 0 20px" }}>Page Not Found</h2>
        <p style={{ color: "#526173", fontSize: "1.1rem", marginBottom: "30px" }}>
          Oops! The page you are looking for doesn't exist or has been moved.
        </p>
        <Link to="/" className="primary-button" style={{ display: "inline-flex", textDecoration: "none" }}>
          Back to Home
        </Link>
      </div>
    </section>
  );
}

export default NotFound;
