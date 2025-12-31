import React, { useState } from 'react';
import axios from 'axios';
import './Accounts.css';

const AccountManagement = () => {
  const [formData, setFormData] = useState({
    name: '',
    platform: 'twitter',
    url: '',
    category: 'economy',
    admin_id: 3  // Set to 3 by default as requested
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const platformOptions = [
    { value: 'twitter', label: 'Twitter' },
    { value: 'facebook', label: 'Facebook' },
    { value: 'instagram', label: 'Instagram' },
    { value: 'youtube', label: 'YouTube' },
    { value: 'linkedin', label: 'LinkedIn' }
  ];

  const categoryOptions = [
    { value: 'economy', label: 'Economy' },
    { value: 'politics', label: 'Politics' },
    { value: 'sports', label: 'Sports' },
   
    { value: 'international_relations', label: 'International Relations' }
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccessMessage('');

    try {
      // Validate URL format
      if (formData.url && !formData.url.match(/^https?:\/\//)) {
        throw new Error('URL must start with http:// or https://');
      }

      const response = await axios.post('http://127.0.0.1:8000/admin/platform_accounts', {
        name: formData.name.trim(),
        platform: formData.platform,
        url: formData.url.trim(),
        category: formData.category,
        admin_id: 3  // Explicitly set to 3 for the API call
      });

      if (response.status === 201) {
        setSuccessMessage('Account successfully added to database!');
        // Reset form
        setFormData({
          name: '',
          platform: 'twitter',
          url: '',
          category: 'economy',
          admin_id: 3
        });
      }
    } catch (err) {
      setError(err.response?.data?.message || err.message || 'Failed to add account');
      console.error('Account creation error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="account-management-container">
      <h1 className="page-title">Add Verification Source</h1>

      <form onSubmit={handleSubmit} className="account-form">
        <div className="form-group">
          <label>Account Holder Name</label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleInputChange}
            required
            minLength="2"
            maxLength="100"
            placeholder="Enter account holder name"
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Platform</label>
            <select
              name="platform"
              value={formData.platform}
              onChange={handleInputChange}
              required
            >
              {platformOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Category</label>
            <select
              name="category"
              value={formData.category}
              onChange={handleInputChange}
              required
            >
              {categoryOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="form-group">
          <label>Account URL</label>
          <input
            type="url"
            name="url"
            value={formData.url}
            onChange={handleInputChange}
            required
            pattern="https?://.+"
            placeholder="https://platform.com/username"
            title="URL must start with http:// or https://"
          />
        </div>

        {error && <div className="error-message">{error}</div>}
        {successMessage && <div className="success-message">{successMessage}</div>}

        <div className="form-actions">
          <button
            type="submit"
            disabled={loading}
            className="submit-button"
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                Creating...
              </>
            ) : (
              'Add Account'
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default AccountManagement;