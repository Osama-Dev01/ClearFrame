import React, { useEffect, useRef, useState } from 'react';
import { FiTrash2, FiRefreshCw, FiTrendingUp, FiCheckCircle } from 'react-icons/fi';
import anime from 'animejs/lib/anime.es.js';
import axios from 'axios';
import './ExpenseList.css';

const MemberList = () => {
  const containerRef = useRef(null);
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deletingId, setDeletingId] = useState(null); // Track which member is being deleted

  const fetchApprovedMembers = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`http://127.0.0.1:8000/admin/approved-members`);
      
      // Keep user_id as number for consistency
      const formattedMembers = response.data.map(member => ({
        id: member.user_id,  // Keep as number
        name: member.username || member.admin_name || 'No Name',
        email: member.email,
        role: member.role === 'admin' ? 'Admin' : 'Member',
        joined: member.created_at
          ? new Date(member.created_at).toISOString().split('T')[0]
          : new Date().toISOString().split('T')[0],
        totalVotes: member.total_votes || 0,
        accuracy: member.accuracy_percentage || 0
      }));
      setMembers(formattedMembers);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch approved members');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteMember = async (memberId, memberName) => {
    // Confirm deletion
    if (!window.confirm(`Are you sure you want to delete "${memberName}"? This action cannot be undone.`)) {
      return;
    }

    try {
      setDeletingId(memberId); // Set which member is being deleted
      
      // Send DELETE request to backend with numeric ID
      await axios.delete(`http://127.0.0.1:8000/admin/delmembers/${memberId}`, {
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      // Remove the member from the state
      setMembers(prevMembers => prevMembers.filter(member => member.id !== memberId));
      
      // Show success message
      alert(`Member "${memberName}" has been deleted successfully.`);
      
    } catch (err) {
      // Handle errors
      const errorMessage = err.response?.data?.detail || 
                           err.response?.data?.message || 
                           'Failed to delete member. Please try again.';
      alert(errorMessage);
    } finally {
      setDeletingId(null); // Reset deleting state
    }
  };

  useEffect(() => {
    fetchApprovedMembers();
    anime({
      targets: containerRef.current,
      opacity: [0, 1],
      translateY: [20, 0],
      easing: 'easeOutExpo',
      duration: 600,
    });
  }, []);

  return (
    <div className="member-list-page" ref={containerRef}>
      <div className="page-header">
        <h1 className="heading">Approved Members</h1>
        <button 
          className="btn-refresh" 
          onClick={fetchApprovedMembers} 
          title="Refresh list"
          disabled={loading}
        >
          <FiRefreshCw className={loading ? 'spinning' : ''} />
        </button>
      </div>

      {loading ? (
        <div className="loading-card card">
          <div className="loading-spinner"></div>
          <p>Loading approved members...</p>
        </div>
      ) : error ? (
        <div className="error-card card">
          <p className="error-message">{error}</p>
          <button className="btn btn-primary" onClick={fetchApprovedMembers}>
            Try Again
          </button>
        </div>
      ) : (
        <div className="members-container">
          {members.length > 0 ? (
            members.map((member) => (
              <div key={member.id} className="member-card card">
                <div className="member-info">
                  <h3>{member.name}</h3>
                  <p>{member.email}</p>
                  
                  <div className="performance-stats">
                    <div className="stat-item">
                      <FiTrendingUp className="stat-icon" />
                      <div>
                        <strong>Total Votes</strong>
                        <span className="stat-value">{member.totalVotes}</span>
                      </div>
                    </div>
                    
                    <div className="stat-item">
                      <FiCheckCircle className="stat-icon" />
                      <div>
                        <strong>Accuracy</strong>
                        <span className={`stat-value ${member.accuracy >= 80 ? 'high' : member.accuracy >= 60 ? 'medium' : 'low'}`}>
                          {member.accuracy}%
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <p>
                    <strong>Role:</strong>{' '}
                    <span className={`role-badge ${member.role.toLowerCase()}`}>{member.role}</span>
                  </p>
                  <p>
                    <strong>Joined:</strong> {new Date(member.joined).toLocaleDateString()}
                  </p>
                </div>

                <div className="member-actions">
                  <button 
                    className="btn btn-danger"
                    onClick={() => handleDeleteMember(member.id, member.name)}
                    disabled={deletingId === member.id} // Only disable for this specific member
                    title="Delete member"
                  >
                    <FiTrash2 /> 
                    {deletingId === member.id ? 'Deleting...' : 'Delete'}
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div className="no-members card">No approved members found.</div>
          )}
        </div>
      )}
    </div>
  );
};

export default MemberList;