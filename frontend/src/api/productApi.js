import apiClient from "./apiClient";


export const checkApiHealth = () => apiClient.get("/health");

export const searchProduct = (payload) => apiClient.post("/search", payload);

export const getReviews = () => apiClient.get("/reviews");

export const getDashboard = () => apiClient.get("/dashboard");
