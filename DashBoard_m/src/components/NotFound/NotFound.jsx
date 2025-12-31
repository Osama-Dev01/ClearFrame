// pages/NotFound.jsx
import React, { useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { FiHome, FiArrowLeft, FiSearch } from 'react-icons/fi';
import anime from 'animejs/lib/anime.es.js';
import './NotFound.css';

const NotFound = () => {
  const pageRef = useRef(null);
  const svgRef = useRef(null);
  const textRef = useRef(null);
  const buttonRefs = useRef([]);

  useEffect(() => {
    // Animate the page entrance
    anime({
      targets: pageRef.current,
      opacity: [0, 1],
      duration: 1000,
      easing: 'easeOutExpo'
    });

    // Animate the 404 text
    anime({
      targets: textRef.current,
      translateY: [-50, 0],
      opacity: [0, 1],
      duration: 1200,
      delay: 300,
      easing: 'easeOutElastic(1, .6)'
    });

    // Animate the SVG elements
    anime({
      targets: '.svg-elem',
      strokeDashoffset: [anime.setDashoffset, 0],
      opacity: [0, 1],
      easing: 'easeInOutSine',
      duration: 1500,
      delay: function(el, i) { return i * 100 + 500 },
    });

    // Animate the floating elements
    anime({
      targets: '.float-element',
      translateY: function() { return anime.random(-15, 15); },
      direction: 'alternate',
      loop: true,
      duration: function() { return anime.random(2000, 4000); },
      easing: 'easeInOutSine',
      delay: function() { return anime.random(0, 1000); }
    });

    // Animate the buttons
    anime({
      targets: buttonRefs.current,
      translateY: [20, 0],
      opacity: [0, 1],
      delay: anime.stagger(150, {start: 1200}),
      easing: 'easeOutExpo',
      duration: 800
    });
  }, []);

  const addButtonRef = (el) => {
    if (el && !buttonRefs.current.includes(el)) {
      buttonRefs.current.push(el);
    }
  };

  return (
    <div className="not-found-page" ref={pageRef}>
      <div className="not-found-container">
        <div className="svg-container" ref={svgRef}>
          <svg viewBox="0 0 600 400" className="not-found-svg">
            {/* Background elements */}
            <circle cx="150" cy="150" r="15" className="svg-elem float-element bg-circle" />
            <circle cx="450" cy="100" r="20" className="svg-elem float-element bg-circle" />
            <circle cx="500" cy="300" r="25" className="svg-elem float-element bg-circle" />
            <circle cx="100" cy="250" r="10" className="svg-elem float-element bg-circle" />
            
            {/* Main 404 graphic */}
            <g className="error-graphic">
              {/* Computer/device */}
              <rect x="200" y="150" width="200" height="150" rx="5" className="svg-elem device" />
              <rect x="210" y="160" width="180" height="110" className="svg-elem screen" />
              <rect x="250" y="300" width="100" height="20" rx="5" className="svg-elem device-base" />
              
              {/* Error face on screen */}
              <circle cx="300" cy="200" r="30" className="svg-elem face" />
              <line x1="285" y1="190" x2="295" y2="190" className="svg-elem face-elem" />
              <line x1="305" y1="190" x2="315" y2="190" className="svg-elem face-elem" />
              <path d="M280,215 Q300,235 320,215" className="svg-elem face-elem" />
              
              {/* Error symbols */}
              <text x="260" y="250" className="svg-elem error-text">ERROR 404</text>
              
              {/* Floating elements around device */}
              <circle cx="150" cy="200" r="10" className="svg-elem float-element data-circle" />
              <circle cx="450" cy="180" r="12" className="svg-elem float-element data-circle" />
              <circle cx="400" cy="120" r="8" className="svg-elem float-element data-circle" />
              <rect x="170" y="150" width="15" height="15" className="svg-elem float-element data-square" />
              <rect x="420" cy="250" width="18" height="18" className="svg-elem float-element data-square" />
              
              {/* Connection lines */}
              <line x1="160" y1="200" x2="200" y2="200" className="svg-elem connection-line" />
              <line x1="400" y1="180" x2="438" y2="180" className="svg-elem connection-line" />
              <line x1="400" y1="120" x2="400" y2="150" className="svg-elem connection-line" />
            </g>
          </svg>
        </div>
        
        <div className="not-found-text" ref={textRef}>
          <h1>404 - Page Not Found</h1>
          <p>Oops! The page you're looking for doesn't exist or has been moved.</p>
        </div>
        
        <div className="not-found-actions">
          <Link to="/" className="btn btn-primary" ref={addButtonRef}>
            <FiHome /> Back to Dashboard
          </Link>
          <Link to="/expenses" className="btn btn-outline" ref={addButtonRef}>
            <FiArrowLeft /> View Expenses
          </Link>
          <Link to="/search" className="btn btn-outline" ref={addButtonRef}>
            <FiSearch /> Search
          </Link>
        </div>
      </div>
    </div>
  );
};

export default NotFound;