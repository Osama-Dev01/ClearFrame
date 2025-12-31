import React, { useEffect, useRef, useState } from 'react';
import { FiCheck, FiX, FiRefreshCw, FiExternalLink } from 'react-icons/fi';
import anime from 'animejs/lib/anime.es.js';
import axios from 'axios';
import './request.css';

const Request = () => {
  const containerRef = useRef(null);
  const tableRowsRef = useRef([]);
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showProfile, setShowProfile] = useState(false);
  const [selectedMember, setSelectedMember] = useState(null);


  const fetchApprovedMembers = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`http://127.0.0.1:8000/admin/approval_requests`);
      const formattedMembers = response.data.map(member => {
        const twitterLink = member.social_links.find(link => link.platform.toLowerCase() === 'twitter');
        const fallbackLink = member.social_links.length > 0 ? member.social_links[0] : null;
        return {
          id: member.user_id.toString(),
          name: member.username || member.admin_name || 'No Name',
          email: member.email,
          role: member.role === 'admin' ? 'Admin' : 'Member',
          occupation: member.occupation || 'N/A',
          city: member.city || 'N/A',
          
          socialLinks: member.social_links || [],
          originalData: member
        };
      });
      setMembers(formattedMembers);
    } catch (err) {
      console.error(err);
      setError('Failed to fetch approval requests');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApprovedMembers();
    anime({
      targets: containerRef.current,
      opacity: [0, 1],
      translateY: [20, 0],
      easing: 'easeOutExpo',
      duration: 700,
    });
  }, []);

  const handleProfile = (member) => {
  setSelectedMember(member);
  setShowProfile(true);
};


  const handleAccept = async (id) => {
    const confirmAdd = window.confirm("Are you sure you want to add this member?");
    if (confirmAdd) {
      try {
        const memberToAccept = members.find(m => m.id === id);
        await axios.post(`http://127.0.0.1:8000/admin/accept_member/${memberToAccept.originalData.user_id}`);
        fetchApprovedMembers();
      } catch (err) {
        alert(`Failed to accept member: ${err.response?.data?.detail || err.message}`);
      }
    }
  };

  const handleDecline = async (id) => {
    const confirmDecline = window.confirm("Are you sure you want to decline this member?");
    if (confirmDecline) {
      try {
        const memberToDecline = members.find(m => m.id === id);
        await axios.post(`http://127.0.0.1:8000/admin/decline_member/${memberToDecline.originalData.user_id}`);
        fetchApprovedMembers();
      } catch (err) {
        alert(`Failed to decline member: ${err.response?.data?.detail || err.message}`);
      }
    }
  };

  return (
    <div className="request-page" ref={containerRef}>
      <div className="page-header">
        <h2>Membership Requests</h2>
        <button className="refresh-btn" onClick={fetchApprovedMembers}>
          <FiRefreshCw /> Refresh
        </button>
      </div>

      {loading ? (
        <div className="loading-state">Loading requests...</div>
      ) : error ? (
        <div className="error-state">{error}</div>
      ) : (
        <div className="card-table">
          <table className="request-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Profile</th>
               
                <th>Actions</th>
              </tr>
            </thead>
                            <tbody>
                  {members.length > 0 ? (
                    members.map((member) => (
                      <tr key={member.id}>
                        <td>{member.name}</td>
                        <td>{member.email}</td>

                        {/* ✅ PROFILE COLUMN */}
                        <td>
                          <button
                            className="profile-btn"
                            onClick={() => handleProfile(member)}
                          >
                            View Profile
                          </button>
                        </td>

                        <td className="action-column">
                          <button className="accept-btn" onClick={() => handleAccept(member.id)}>
                            <FiCheck /> Accept
                          </button>
                          <button className="decline-btn" onClick={() => handleDecline(member.id)}>
                            <FiX /> Decline
                          </button>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="4" className="no-data">No membership requests found.</td>
                    </tr>
                  )}
                </tbody>

          </table>

        {showProfile && selectedMember && (
  <div className="profile-modal-overlay" onClick={() => setShowProfile(false)}>
    <div className="profile-modal" onClick={(e) => e.stopPropagation()}>
      {/* Header */}
      <div className="profile-modal-header">
        <h3>
          Member Profile
          <span className={`profile-role-badge ${selectedMember.role.toLowerCase()}`}>
            {selectedMember.role}
          </span>
        </h3>
        <button 
          className="modal-close-btn" 
          onClick={() => setShowProfile(false)}
          aria-label="Close"
        >
          ×
        </button>
      </div>

      {/* Content */}
      <div className="profile-modal-content">
        {/* Basic Info Section */}
        <div className="profile-section">
          <div className="profile-section-title">
            Basic Information
          </div>
          
          <div className="profile-info-item">
            <span className="info-label">Full Name</span>
            <span className="info-value">{selectedMember.name}</span>
          </div>
          
          <div className="profile-info-item">
            <span className="info-label">Email Address</span>
            <span className="info-value">{selectedMember.email}</span>
          </div>
          
          <div className="profile-info-item">
            <span className="info-label">Occupation</span>
            <span className="info-value">{selectedMember.occupation}</span>
          </div>
          
          <div className="profile-info-item">
            <span className="info-label">City</span>
            <span className="info-value">{selectedMember.city}</span>
          </div>
        </div>

        {/* Social Links Section */}
        <div className="profile-section">
          <div className="profile-section-title">
            Social Profiles
          </div>
          
          {selectedMember.socialLinks.length > 0 ? (
            <div className="social-section">
              <div className="social-links-grid">
                {selectedMember.socialLinks.map((link, idx) => {
                  // Determine icon class based on platform
                  const platformClass = link.platform.toLowerCase();
                  return (
                    <a 
                      key={idx}
                      href={link.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="social-link-item"
                    >
                      <div className={`social-icon ${platformClass}`}>
                        {platformClass.charAt(0).toUpperCase()}
                      </div>
                      <div className="social-link-info">
                        <div className="social-platform">
                          {link.platform}
                        </div>
                        <div className="social-url">
                          {link.url.length > 25 ? `${link.url.substring(0, 25)}...` : link.url}
                        </div>
                      </div>
                    </a>
                  );
                })}
              </div>
            </div>
          ) : (
            <div className="profile-info-item">
              <span className="info-label">No Social Links</span>
              <span className="info-value" style={{ opacity: 0.7 }}>
                This member hasn't added any social profiles
              </span>
            </div>
          )}
        </div>

        {/* Close Button */}
        <button className="close-btn" onClick={() => setShowProfile(false)}>
          Close Profile
        </button>
      </div>
    </div>
  </div>
)}

        </div>
      )}
    </div>
  );
};

export default Request;
