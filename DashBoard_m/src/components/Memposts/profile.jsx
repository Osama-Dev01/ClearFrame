import React, { useEffect, useState } from "react";
import axios from "axios";
import { useMember } from '../Auth/MemberContext';
import "./profile.css";

const Profile = () => {
  const [profileData, setProfileData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { member } = useMember();

  useEffect(() => {
    const fetchProfileData = async () => {
      setLoading(true);
      setError(null);

      if (!member?.id) {
        setError("No member ID found. Please log in.");
        setLoading(false);
        return;
      }

      try {
        const response = await axios.get(`http://127.0.0.1:8000/member/profile/${member.id}`);
        setProfileData(response.data);
      } catch (err) {
        console.error("Error fetching profile data:", err);
        setError("Failed to load profile data. Please try again later.");
      } finally {
        setLoading(false);
      }
    };

    fetchProfileData();
  }, [member]);

  const handleRetry = () => {
    window.location.reload();
  };

  if (loading) {
    return (
      <div className="activity-container">
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading profile...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="activity-container">
        <div className="error-state">
          <div className="error-icon">!</div>
          <h3>Error Loading Profile</h3>
          <p>{error}</p>
          <button className="retry-button" onClick={handleRetry}>
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!profileData) {
    return (
      <div className="activity-container">
        <div className="empty-state">
          <h3>No Profile Found</h3>
          <p>We couldn't find your profile information.</p>
          <p className="empty-subtext">Please try again later or contact support.</p>
        </div>
      </div>
    );
  }

  const profileSections = [
    {
      title: "Personal Information",
      items: [
        { label: "Username", value: profileData.username },
        { label: "Email", value: profileData.email },
        { label: "City", value: profileData.city },
        { label: "Occupation", value: profileData.occupation }
      ]
    },
    {
      title: "Social Information",
      items: [
        { label: "Platform", value: profileData.socialPlatform },
        { 
          label: "Social URL", 
          value: profileData.socialUrl,
          isLink: true 
        }
      ]
    }
  ];

  return (
    <div className="profile-container">
      {/* Page Header */}
      <div className="profile-page-header">
        <div className="profile-header-content">
          <h2 className="profile-page-heading">My Profile</h2>
          <p className="profile-page-subtitle">Manage your personal information and settings</p>
        </div>
        
      </div>

      {/* Single Unified Profile Card */}
      <div className="profile-main-card">
        {/* Profile Header with Avatar */}
        <div className="profile-card-header">
          <div className="profile-avatar-container">
            <div className="profile-avatar">
              {profileData.username?.charAt(0).toUpperCase() || 'U'}
            </div>
            <div className="profile-status-badge"></div>
          </div>
          <div className="profile-header-info">
            <h3 className="profile-user-name">{profileData.username || 'User'}</h3>
            <p className="profile-user-email">{profileData.email || 'email@example.com'}</p>
            <div className="profile-member-badge">
              Active Member
            </div>
          </div>
        </div>

        <div className="profile-main-divider"></div>

        {/* Profile Sections */}
        {profileSections.map((section, sectionIndex) => (
          <div key={sectionIndex} className="profile-section">
            <div className="profile-section-header">
              <h4 className="profile-section-title">{section.title}</h4>
            </div>
            
            <div className="profile-info-grid">
              {section.items.map((item, itemIndex) => (
                <div key={itemIndex} className="profile-info-item">
                  <div className="profile-info-label">
                    {item.label}
                  </div>
                  <div className="profile-info-value">
                    {item.isLink && item.value ? (
                      <a 
                        href={item.value} 
                        target="_blank" 
                        rel="noopener noreferrer" 
                        className="profile-social-link"
                      >
                        {item.value.length > 40 ? item.value.substring(0, 40) + '...' : item.value}
                        <span className="profile-link-icon">↗</span>
                      </a>
                    ) : (
                      <span>{item.value || 'Not provided'}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
            
            {sectionIndex < profileSections.length - 1 && (
              <div className="profile-section-divider"></div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default Profile;