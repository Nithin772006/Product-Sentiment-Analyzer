import React, { useState } from "react";

function SearchBar({ onSearch, placeholder = "Search for a product (e.g. wireless headphones)..." }) {
  const [query, setQuery] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!query.trim()) {
      setError("Please enter a valid product keyword.");
      return;
    }
    setError("");
    onSearch(query.trim());
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter") {
      handleSubmit(event);
    }
  };

  return (
    <div className="search-bar-container">
      <form className="search-bar-form" onSubmit={handleSubmit}>
        <div className="input-group">
          <input
            type="text"
            className={`search-input ${error ? "has-error" : ""}`}
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              if (e.target.value.trim()) setError("");
            }}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            aria-label="Product Search Query"
          />
          <button type="submit" className="primary-button search-button">
            Search
          </button>
        </div>
        {error && <p className="error-text" role="alert">{error}</p>}
      </form>
    </div>
  );
}

export default SearchBar;
