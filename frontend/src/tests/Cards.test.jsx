import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, test, expect } from "vitest";

import ProductCard from "../components/ProductCard";
import ReviewCard from "../components/ReviewCard";
import StatisticsCard from "../components/StatisticsCard";

describe("Cards Components", () => {
  describe("ProductCard", () => {
    const mockProduct = {
      name: "Super Sound Pro",
      brand: "BrandX",
      price: "$120.00",
      rating: 4.5,
      reviewCount: 99,
      image: "http://example.com/image.jpg",
    };

    test("renders product details correctly", () => {
      render(<ProductCard product={mockProduct} />);

      expect(screen.getByText("Super Sound Pro")).toBeInTheDocument();
      expect(screen.getByText("BrandX")).toBeInTheDocument();
      expect(screen.getByText("$120.00")).toBeInTheDocument();
      expect(screen.getByText("4.5")).toBeInTheDocument();
      expect(screen.getByText("(99 reviews)")).toBeInTheDocument();
      
      const img = screen.getByRole("img");
      expect(img).toBeInTheDocument();
      expect(img).toHaveAttribute("src", mockProduct.image);
    });
  });

  describe("ReviewCard", () => {
    const mockReview = {
      reviewerName: "John Doe",
      title: "Excellent buy",
      reviewText: "Highly recommend it to everyone.",
      rating: 5,
      sentiment: "positive",
      sentimentScore: 0.95,
      date: "2026-06-30",
    };

    test("renders reviewer details and sentiment badge", () => {
      render(<ReviewCard review={mockReview} />);

      expect(screen.getByText("John Doe")).toBeInTheDocument();
      expect(screen.getByText("Excellent buy")).toBeInTheDocument();
      expect(screen.getByText("Highly recommend it to everyone.")).toBeInTheDocument();
      expect(screen.getByText(/positive/i)).toBeInTheDocument();
      expect(screen.getByText(/95%/i)).toBeInTheDocument();
      expect(screen.getByText("2026-06-30")).toBeInTheDocument();
    });
  });

  describe("StatisticsCard", () => {
    test("renders metrics title and value", () => {
      render(
        <StatisticsCard
          title="Total Audited reviews"
          value="1,248"
          helperText="Aggregated count"
          icon="reviews"
        />
      );

      expect(screen.getByText("Total Audited reviews")).toBeInTheDocument();
      expect(screen.getByText("1,248")).toBeInTheDocument();
      expect(screen.getByText("Aggregated count")).toBeInTheDocument();
    });
  });
});
