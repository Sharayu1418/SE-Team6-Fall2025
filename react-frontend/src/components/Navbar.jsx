// react-frontend/src/components/Navbar.jsx
import React from 'react';
import { Link } from 'react-router-dom'; // <-- 1. Import Link

export default function Navbar() {
  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-dark fixed-top">
      <div className="container-fluid">
        <Link className="navbar-brand" to="/"> {/* <-- 2. Use Link and 'to' */}
          SmartCache AI
        </Link>
        {/* ... (toggler button is the same) ... */}
        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav me-auto mb-2 mb-lg-0">
            <li className="nav-item">
              <Link className="nav-link" to="/">Dashboard</Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/commutes">Commutes</Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/sources">Sources</Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/downloads">Downloads</Link>
            </li>
          </ul>
          <span className="navbar-text">
            shreyasgowda
          </span>
        </div>
      </div>
    </nav>
  );
}