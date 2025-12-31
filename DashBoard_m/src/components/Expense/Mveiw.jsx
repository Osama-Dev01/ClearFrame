import React, { useEffect, useRef, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FiX, FiUser, FiMail, FiBriefcase, FiCheckCircle, FiTarget } from 'react-icons/fi';
import anime from 'animejs/lib/anime.es.js';
import axios from 'axios';
import './Mveiw.css';

const MView = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const modalRef = useRef(null);
  const [member, setMember] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

 
  const handleClose = () => {
    anime({
      targets: '.modal-overlay',
      opacity: [1, 0],
      duration: 250,
      easing: 'easeInQuad'
    });

    anime({
      targets: modalRef.current,
      opacity: [1, 0],
      scale: [1, 0.95],
      duration: 250,
      easing: 'easeInExpo',
      complete: () => navigate(-1)
    });
  };

  if (loading) {
    return (
      <div className="modal-overlay">
        <div className="modal-content" ref={modalRef}>
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Loading member details...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="modal-overlay">
        <div className="modal-content" ref={modalRef}>
          <button className="close-btn" onClick={handleClose}>
            <FiX />
          </button>
          <div className="error-state">
            <p>{error}</p>
            <button className="btn-retry" onClick={() => window.location.reload()}>
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="modal-overlay" onClick={handleClose}>
      <div className="modal-content" ref={modalRef} onClick={(e) => e.stopPropagation()}>
        <button className="close-btn" onClick={handleClose}>
          <FiX />
        </button>

        <div className="modal-header">
          <div className="avatar-circle">
            {member.name.charAt(0).toUpperCase()}
          </div>
          <h2>{member.name}</h2>
          <span className={`role-tag ${member.role}`}>{member.role}</span>
        </div>

        <div className="modal-body">
          <div className="info-item">
            <div className="info-icon">
              <FiMail />
            </div>
            <div className="info-content">
              <label>Email Address</label>
              <p>{member.email}</p>
            </div>
          </div>

          <div className="info-item">
            <div className="info-icon">
              <FiBriefcase />
            </div>
            <div className="info-content">
              <label>Occupation</label>
              <p>{member.occupation}</p>
            </div>
          </div>

          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon">
                <FiCheckCircle />
              </div>
              <div className="stat-content">
                <label>Total Votes Cast</label>
                <h3>{member.totalVotes}</h3>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon accuracy">
                <FiTarget />
              </div>
              <div className="stat-content">
                <label>Vote Accuracy</label>
                <h3>{member.voteAccuracy}%</h3>
              </div>
            </div>
          </div>

          <div className="member-joined">
            <small>Member since: {new Date(member.joined).toLocaleDateString('en-US', { 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric' 
            })}</small>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MView;