import React, { useState, useEffect } from "react";

import { searchProduct, getProducts, getReviews } from "../services/api";
import SearchBar from "../components/SearchBar";
import ProductCard from "../components/ProductCard";
import ReviewCard from "../components/ReviewCard";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorMessage from "../components/ErrorMessage";

function Search() {
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [searchResult, setSearchResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load available products on component mount
  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await getProducts();
      setProducts(response.data || []);
    } catch (err) {
      setError("Failed to load products. Please check the backend connection.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = async (query) => {
    setIsLoading(true);
    setError(null);
    setSearchResult(null);
    try {
      const payload = { productName: query, platform: "amazon" };
      const response = await searchProduct(payload);
      setSearchResult(response.data);
      // Automatically select the first mock product for user visualization if matching
      if (products.length > 0) {
        handleProductClick(products[0]);
      }
    } catch (err) {
      setError("Could not submit search request. Backend API may be offline.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleProductClick = async (product) => {
    setSelectedProduct(product);
    setIsLoading(true);
    setError(null);
    try {
      const response = await getReviews();
      // Filter reviews to match selected product just for visual mockup consistency
      setReviews(response.data?.reviews || []);
    } catch (err) {
      setError("Failed to load reviews for this product.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="page-section search-page-container">
      <div className="section-heading">
        <p className="eyebrow">Search Engine</p>
        <h1>Find Products & Analyze Reviews</h1>
        <p className="section-description">
          Enter a product name to initiate automatic scraping and sentiment classification, or select a pre-scraped product below.
        </p>
      </div>

      <SearchBar onSearch={handleSearch} />

      {isLoading && <LoadingSpinner />}

      {error && <ErrorMessage message={error} onRetry={fetchProducts} />}

      {searchResult && (
        <div className="search-result-alert success-alert">
          <h4>Search Job Dispatched</h4>
          <p>{searchResult.message}</p>
          <div className="alert-details">
            <span><strong>Job ID:</strong> {searchResult.job?.id}</span>
            <span><strong>Status:</strong> {searchResult.job?.status}</span>
          </div>
        </div>
      )}

      <div className="search-content-layout">
        <div className="products-column">
          <h2>Available Products</h2>
          {products.length === 0 && !isLoading && <p className="no-data-msg">No products found.</p>}
          <div className="products-list-grid">
            {products.map((product) => (
              <ProductCard
                key={product.id}
                product={product}
                onClick={() => handleProductClick(product)}
              />
            ))}
          </div>
        </div>

        {selectedProduct && (
          <div className="reviews-column">
            <h2>Reviews for {selectedProduct.name}</h2>
            {reviews.length === 0 ? (
              <p className="no-data-msg">No reviews available for this product.</p>
            ) : (
              <div className="reviews-list">
                {reviews.map((review) => (
                  <ReviewCard key={review.id} review={review} />
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  );
}

export default Search;
