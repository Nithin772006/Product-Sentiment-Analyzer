import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, test, expect } from "vitest";

import Navbar from "../components/Navbar";

describe("Navbar Component", () => {
  test("renders logo and brand name", () => {
    render(
      <MemoryRouter>
        <Navbar />
      </MemoryRouter>
    );

    const brandLink = screen.getByText(/Product Sentiment Analyzer/i);
    expect(brandLink).toBeInTheDocument();
  });

  test("renders all navigation links", () => {
    render(
      <MemoryRouter>
        <Navbar />
      </MemoryRouter>
    );

    const homeLink = screen.getByRole("link", { name: /Home/i });
    const searchLink = screen.getByRole("link", { name: /Search/i });
    const dashboardLink = screen.getByRole("link", { name: /Dashboard/i });

    expect(homeLink).toBeInTheDocument();
    expect(searchLink).toBeInTheDocument();
    expect(dashboardLink).toBeInTheDocument();
  });

  test("toggles responsive hamburger menu", () => {
    render(
      <MemoryRouter>
        <Navbar />
      </MemoryRouter>
    );

    const toggleButton = screen.getByRole("button", { name: /Toggle navigation menu/i });
    expect(toggleButton).toBeInTheDocument();
    expect(toggleButton).toHaveAttribute("aria-expanded", "false");

    fireEvent.click(toggleButton);
    expect(toggleButton).toHaveAttribute("aria-expanded", "true");
  });
});
