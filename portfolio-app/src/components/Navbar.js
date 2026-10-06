import React from 'react';
import { NavLink } from 'react-router-dom';

const links = [
  { to: '/', label: 'Home' },
  { to: '/about', label: 'About' },
  { to: '/projects', label: 'Projects' },
  { to: '/contact', label: 'Contact' },
];

export default function Navbar() {
  return (
    <nav className="navbar navbar-expand-md navbar-dark bg-dark fixed-top" aria-label="Main navigation">
      <div className="container">
        <NavLink className="navbar-brand fw-bold" to="/">Sanskar B.</NavLink>
        <button
          className="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#mainNav"
          aria-controls="mainNav"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon" />
        </button>
        <div className="collapse navbar-collapse" id="mainNav">
          <ul className="navbar-nav ms-auto">
            {links.map(({ to, label }) => (
              <li className="nav-item" key={to}>
                <NavLink end className="nav-link" to={to}>{label}</NavLink>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </nav>
  );
}
