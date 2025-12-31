import React, { useState, useEffect, useRef } from 'react';
import { Link, useLocation } from 'react-router-dom';
import anime from 'animejs/lib/anime.es.js';
import './Msidebar.css';
import MediaQuery from 'react-responsive';

// ✅ Import the custom hook
import { useMember } from '../Auth/MemberContext';

function Msidebar() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const location = useLocation();
  const sidebarRef = useRef(null);
  const linksRef = useRef([]);

  // ✅ Use the logout function from context
  const { logoutMember } = useMember();

  // Set active tab based on current route
  useEffect(() => {
    const path = location.pathname;
    if (path === '/member' || path === '/member/') setActiveTab('dashboard');
    else if (path === '/member/posts') setActiveTab('posts');
    else if (path === '/member/activity') setActiveTab('activity');
    else if (path === '/member/profile') setActiveTab('profile');
  }, [location]);

  // Animation effects
  useEffect(() => {
    if (sidebarRef.current) {
      anime({
        targets: sidebarRef.current,
        translateX: [-250, 0],
        opacity: [0, 1],
        duration: 800,
        easing: 'easeOutExpo'
      });

      anime({
        targets: linksRef.current,
        translateX: [-20, 0],
        opacity: [0, 1],
        delay: anime.stagger(100, { start: 300 }),
        easing: 'easeOutExpo'
      });
    }
  }, []);

  const addToLinksRef = (el) => {
    if (el && !linksRef.current.includes(el)) {
      linksRef.current.push(el);
    }
  };

  const handleLogout = () => {
    logoutMember(); // ✅ Clear state and localStorage
    window.location.href = '/m_login';
  };

  const navItems = [
    { id: 'dashboard', icon: '🏠', label: 'Dashboard', path: '/member' },
    { id: 'posts', icon: '📋', label: 'Unverified Posts', path: '/member/posts' },
    { id: 'activity', icon: '📈', label: 'My Activity', path: '/member/activity' },
    { id: 'profile', icon: '👤', label: 'Profile', path: '/member/profile' }
  ];

  return (
    <MediaQuery minWidth={769}>
      <aside className="sidebar" ref={sidebarRef}>
        <div className="sidebar-header">
          <div className="logo">
            <div className="logo-icon">✓</div>
            <span className="logo-text">ClearFrame</span>
          </div>
          <p className="logo-tagline">Verification Portal</p>
        </div>

        <nav className="sidebar-nav">
          {navItems.map(item => (
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

export default Msidebar;