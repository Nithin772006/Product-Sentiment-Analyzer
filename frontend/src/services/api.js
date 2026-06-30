import axios from "axios";

// Read environment variables (supports Vite and standard CRA formats)
const BASE_URL = import.meta.env?.VITE_API_BASE_URL || 
                 process.env?.REACT_APP_API_URL || 
                 "http://localhost:5000/api";

const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Reusable mock products for getProducts
const MOCK_PRODUCTS = [
  {
    id: "prod-001",
    name: "Sample Wireless Headphones",
    brand: "SoundPro",
    price: "$99.99",
    rating: 4.1,
    reviewCount: 128,
    image: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&auto=format&fit=crop&q=60"
  },
  {
    id: "prod-002",
    name: "Smart Fitness Watch",
    brand: "ActiveLife",
    price: "$149.99",
    rating: 4.5,
    reviewCount: 256,
    image: "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&auto=format&fit=crop&q=60"
  },
  {
    id: "prod-003",
    name: "Ergonomic Office Chair",
    brand: "ComfortSeat",
    price: "$199.99",
    rating: 3.8,
    reviewCount: 64,
    image: "https://images.unsplash.com/photo-1580481072645-022f9a6dbf27?w=500&auto=format&fit=crop&q=60"
  }
];

export const healthCheck = () => apiClient.get("/health");

export const searchProduct = (payload) => apiClient.post("/search", payload);

// Since there is no /products endpoint in Flask backend, we provide a clean, mocked function
export const getProducts = () => {
  return Promise.resolve({ data: MOCK_PRODUCTS });
};

export const getReviews = () => apiClient.get("/reviews");

export const getDashboard = () => apiClient.get("/dashboard");

export default {
  healthCheck,
  searchProduct,
  getProducts,
  getReviews,
  getDashboard,
};
