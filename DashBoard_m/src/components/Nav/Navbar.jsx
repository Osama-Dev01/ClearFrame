import React, { useEffect, useRef } from 'react';
import { NavLink } from 'react-router-dom'; 
import anime from 'animejs/lib/anime.es.js';
import './Navbar.css';
import logo from '../../logo.svg'; // Make sure this path is correct

const Navbar = () => {
  const navbarRef = useRef(null);

  useEffect(() => {
    // The entrance animation is a great touch, so we keep it.
    anime({
      targets: navbarRef.current,
      translateY: [-70, 0], // Match the navbar height
      opacity: [0, 1],
      duration: 800,
      easing: 'easeOutExpo'
    });
  }, []);

  return (
    <nav className="navbar" ref={navbarRef}>
      <div className="navbar-container">
        {/* --- LEFT SECTION --- */}
        <div className="navbar-left">
          <NavLink to="/" className="logo">
            <img src={logo} alt="ClearFrame Logo" className="logo-image" />
            ClearFrame<span>.</span>
          </NavLink>
        </div>

        {/* --- RIGHT SECTION --- */}
        <div className="navbar-right">
          {/* This is the new, non-clickable, bold page title */}
          <div className="navbar-title">
            Dashboard
          </div>
          
          {/* A placeholder for a future user profile dropdown */}
          <div className="navbar-profile">
            {/* Example: <ProfileIcon user={...} /> */}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;