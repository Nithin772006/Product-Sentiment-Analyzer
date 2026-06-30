import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, test, expect, vi } from "vitest";

import SearchBar from "../components/SearchBar";

describe("SearchBar Component", () => {
  test("renders input and search button", () => {
    render(<SearchBar onSearch={() => {}} />);
    
    const input = screen.getByPlaceholderText(/Search for a product/i);
    const button = screen.getByRole("button", { name: /Search/i });

    expect(input).toBeInTheDocument();
    expect(button).toBeInTheDocument();
  });

  test("submits valid query", () => {
    const handleSearch = vi.fn();
    render(<SearchBar onSearch={handleSearch} />);

    const input = screen.getByPlaceholderText(/Search for a product/i);
    const button = screen.getByRole("button", { name: /Search/i });

    fireEvent.change(input, { target: { value: "wireless headphones" } });
    fireEvent.click(button);

    expect(handleSearch).toHaveBeenCalledWith("wireless headphones");
  });

  test("shows error message for empty search submit", () => {
    const handleSearch = vi.fn();
    render(<SearchBar onSearch={handleSearch} />);

    const button = screen.getByRole("button", { name: /Search/i });
    fireEvent.click(button);

    const errorMessage = screen.getByRole("alert");
    expect(errorMessage).toBeInTheDocument();
    expect(errorMessage).toHaveTextContent("Please enter a valid product keyword.");
    expect(handleSearch).not.toHaveBeenCalled();
  });
});
