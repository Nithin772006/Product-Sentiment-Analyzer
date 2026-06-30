import { describe, test, expect, vi, beforeEach } from "vitest";
import axios from "axios";

// Mock the axios module
vi.mock("axios", () => {
  const mockAxios = {
    get: vi.fn(),
    post: vi.fn(),
    create: vi.fn().mockReturnThis(),
    interceptors: {
      response: {
        use: vi.fn(),
      },
    },
  };
  return {
    default: mockAxios,
  };
});

// Import the api service after mocking
import api from "../services/api";

describe("API Service Functions", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test("healthCheck invokes get on /health", async () => {
    axios.get.mockResolvedValueOnce({ data: { status: "ok" } });
    const res = await api.healthCheck();
    expect(axios.get).toHaveBeenCalledWith("/health");
    expect(res.data.status).toBe("ok");
  });

  test("searchProduct invokes post on /search with payload", async () => {
    axios.post.mockResolvedValueOnce({ data: { message: "Job created" } });
    const payload = { productName: "watch", platform: "flipkart" };
    const res = await api.searchProduct(payload);
    expect(axios.post).toHaveBeenCalledWith("/search", payload);
    expect(res.data.message).toBe("Job created");
  });

  test("getProducts returns mock products list successfully", async () => {
    const res = await api.getProducts();
    expect(res.data).toBeInstanceOf(Array);
    expect(res.data.length).toBeGreaterThan(0);
    expect(res.data[0]).toHaveProperty("name");
  });

  test("getReviews invokes get on /reviews", async () => {
    axios.get.mockResolvedValueOnce({ data: { reviews: [] } });
    const res = await api.getReviews();
    expect(axios.get).toHaveBeenCalledWith("/reviews");
    expect(res.data.reviews).toEqual([]);
  });

  test("getDashboard invokes get on /dashboard", async () => {
    axios.get.mockResolvedValueOnce({ data: { summary: {} } });
    const res = await api.getDashboard();
    expect(axios.get).toHaveBeenCalledWith("/dashboard");
    expect(res.data.summary).toEqual({});
  });
});
