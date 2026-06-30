import React, { useState } from "react";
import { NavLink } from "react-router-dom";

function Navbar() {
  const [isOpen, setIsOpen] = useState(false);

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  const closeMenu = () => {
    setIsOpen(false);
  };

  return (
    <header className="site-header">
      <nav className="navbar">
        <NavLink to="/" className="brand" onClick={closeMenu}>
          <span className="logo-icon">📊</span> Product Sentiment Analyzer
        </NavLink>

        {/* Hamburger Menu Icon */}
        <button 
          className={`menu-toggle ${isOpen ? "open" : ""}`} 
          onClick={toggleMenu}
          aria-label="Toggle navigation menu"
          aria-expanded={isOpen}
        >
          <span className="hamburger-bar"></span>
          <span className="hamburger-bar"></span>
          <span className="hamburger-bar"></span>
        </button>

        {/* Navigation Links */}
        <div className={`nav-links ${isOpen ? "show" : ""}`}>
          <NavLink to="/" className={({ isActive }) => isActive ? "active" : ""} onClick={closeMenu}>
            Home
          </NavLink>
          <NavLink to="/search" className={({ isActive }) => isActive ? "active" : ""} onClick={closeMenu}>
            Search
          </NavLink>
          <NavLink to="/dashboard" className={({ isActive }) => isActive ? "active" : ""} onClick={closeMenu}>
            Dashboard
          </NavLink>
        </div>
      </nav>
    </header>
  );
}

export default Navbar;
