import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { describe, test, expect, vi } from "vitest";

import Dashboard from "../pages/Dashboard";
import * as api from "../services/api";

// Mock the api module methods
vi.mock("../services/api", () => {
  return {
    getDashboard: vi.fn(),
    getProducts: vi.fn(),
  };
});

describe("Dashboard Page", () => {
  const mockDashboardData = {
    summary: {
      totalReviews: 128,
      averageRating: 4.1,
      positivePercentage: 68,
      neutralPercentage: 19,
      negativePercentage: 13,
    },
    sentimentDistribution: {
      positive: 87,
      neutral: 24,
      negative: 17,
    },
    ratingDistribution: {
      "1": 8,
      "2": 9,
      "3": 24,
      "4": 37,
      "5": 50,
    },
    recentKeywords: ["battery", "quality", "price"],
  };

  test("renders loading spinner initially", () => {
    vi.mocked(api.getDashboard).mockReturnValue(new Promise(() => {})); // Never resolves
    vi.mocked(api.getProducts).mockReturnValue(new Promise(() => {}));

    render(<Dashboard />);
    expect(screen.getByRole("status")).toBeInTheDocument();
  });

  test("renders error message on api failure", async () => {
    vi.mocked(api.getDashboard).mockRejectedValue(new Error("API Error"));
    vi.mocked(api.getProducts).mockRejectedValue(new Error("API Error"));

    render(<Dashboard />);

    await waitFor(() => {
      expect(screen.getByRole("alert")).toBeInTheDocument();
      expect(screen.getByText(/Failed to connect to the backend/i)).toBeInTheDocument();
    });
  });

  test("renders statistics cards and keywords list on success", async () => {
    vi.mocked(api.getDashboard).mockResolvedValue({ data: mockDashboardData });
    vi.mocked(api.getProducts).mockResolvedValue({ data: [{ id: "1" }, { id: "2" }] });

    render(<Dashboard />);

    await waitFor(() => {
      // Check for StatisticsCard title rendering
      expect(screen.getByText("Total Products")).toBeInTheDocument();
      // Check total products count value
      expect(screen.getByText("2")).toBeInTheDocument();

      // Check total reviews count value
      expect(screen.getByText("128")).toBeInTheDocument();

      // Check average rating score
      expect(screen.getByText("4.1 / 5")).toBeInTheDocument();

      // Check keyword tags
      expect(screen.getByText("#battery")).toBeInTheDocument();
      expect(screen.getByText("#quality")).toBeInTheDocument();
      expect(screen.getByText("#price")).toBeInTheDocument();
    });
  });
});
