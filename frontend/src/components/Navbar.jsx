import { NavLink } from "react-router-dom";


function Navbar() {
  return (
    <header className="site-header">
      <nav className="navbar">
        <NavLink to="/" className="brand">
          Product Sentiment Analyzer
        </NavLink>
        <div className="nav-links">
          <NavLink to="/">Home</NavLink>
          <NavLink to="/search">Search</NavLink>
          <NavLink to="/dashboard">Dashboard</NavLink>
        </div>
      </nav>
    </header>
  );
}

export default Navbar;
