// components/Sidebar.jsx
import React, { useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import {
  RiDashboardLine,
  RiLogoutBoxLine,
} from 'react-icons/ri';
import { FaTwitter } from 'react-icons/fa';
import anime from 'animejs/lib/anime.es.js';
import './Memsidebar.css';
import MediaQuery from 'react-responsive';

// ✅ Import the custom hook
import { useMember } from '../Auth/MemberContext';// update path if needed

const Memsidebar = ({ menu }) => {
  const sidebarRef = useRef(null);
  const linksRef = useRef([]);

  // ✅ Use the logout function from context
  const { logoutMember } = useMember();

  useEffect(() => {
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
  }, [menu]);

  const addToLinksRef = (el) => {
    if (el && !linksRef.current.includes(el)) {
      linksRef.current.push(el);
    }
  };

  const handleLogout = () => {
    logoutMember(); // ✅ Clear state and localStorage
    window.location.href = '/login'; // or use navigate('/login') if using useNavigate
  };

  return (
    <MediaQuery minWidth={769}>
      <div className="sidebar" ref={sidebarRef}>
        <div className="sidebar-header">
          <h3>Wellcome Member</h3>
        </div>
        <div className="sidebar-menu">
          <Link to="/member" className="menu-item" ref={addToLinksRef}>
            <RiDashboardLine className="menu-icon" />
            <span>Dashboard</span>
          </Link>
          <Link to="/member/posts" className="menu-item" ref={addToLinksRef}>
            <FaTwitter className="menu-icon" />
            <span>Unverified Posts</span>
          </Link>
        </div>
        <div className="sidebar-footer">
          <button className="menu-item logout-button" ref={addToLinksRef} onClick={handleLogout}>
            <RiLogoutBoxLine className="menu-icon" />
            <span>Logout</span>
          </button>
        </div>
      </div>
    </MediaQuery>
  );
};

export default Memsidebar;
