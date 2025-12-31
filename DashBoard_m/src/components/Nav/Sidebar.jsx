import React, { useState, useEffect, useRef } from 'react';
import { Link, useLocation } from 'react-router-dom';
import anime from 'animejs/lib/anime.es.js';
import MediaQuery from 'react-responsive';
import './Sidebar.css';

function Sidebar() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const location = useLocation();
  const sidebarRef = useRef(null);
  const linksRef = useRef([]);

  const addToLinksRef = (el) => {
    if (el && !linksRef.current.includes(el)) {
      linksRef.current.push(el);
    }
  };

  // Set active tab based on route
  useEffect(() => {
    const path = location.pathname;
    if (path === '/' || path === '/admin') setActiveTab('dashboard');
    else if (path === '/expenses') setActiveTab('members');
    else if (path === '/request') setActiveTab('requests');
  }, [location]);

  // Sidebar entrance animation
  useEffect(() => {
    if (sidebarRef.current) {
      anime({
        targets: sidebarRef.current,
        translateX: [-250, 0],
        opacity: [0, 1],
        duration: 800,
        easing: 'easeOutExpo',
      });

      anime({
        targets: linksRef.current,
        translateX: [-20, 0],
        opacity: [0, 1],
        delay: anime.stagger(100, { start: 300 }),
        easing: 'easeOutExpo',
      });
    }
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('adminAuth');
    window.location.href = '/login';
  };

  const navItems = [
    { id: 'dashboard', icon: '📊', label: 'Dashboard', path: '/' },
    { id: 'members', icon: '👥', label: 'Members', path: '/expenses' },
    { id: 'requests', icon: '📩', label: 'Requests', path: '/request' },
  ];

  return (
    <MediaQuery minWidth={769}>
      <aside className="admin-sidebar" ref={sidebarRef}>
        <div className="sidebar-header">
          <div className="logo">
            <div className="logo-icon">✓</div>
            <span className="logo-text">ClearFrame</span>
          </div>
          <p className="logo-tagline">Control Dashboard</p>
        </div>

        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <Link
              key={item.id}
              to={item.path}
              className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
              ref={addToLinksRef}
              onClick={() => setActiveTab(item.id)}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </Link>
          ))}
        </nav>

        <div className="sidebar-footer">
          <button className="logout-btn" onClick={handleLogout} ref={addToLinksRef}>
            <span className="nav-icon">🚪</span>
            <span className="nav-label">Logout</span>
          </button>
        </div>
      </aside>
    </MediaQuery>
  );
}

export default Sidebar;
