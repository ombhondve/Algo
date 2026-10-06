import React from 'react';
import { Link } from 'react-router-dom';

export default function Hero() {
  return (
    <header id="home" className="hero">
      <div className="container">
        <h1>Hi, I'm Sanskar Ravindra Bhondve</h1>
        <p className="lead my-3">Frontend developer crafting fast, responsive and accessible web experiences.</p>
        <Link to="/projects" className="btn btn-light btn-lg me-2">View Projects</Link>
        <Link to="/contact" className="btn btn-outline-light btn-lg">Contact Me</Link>
      </div>
    </header>
  );
}
