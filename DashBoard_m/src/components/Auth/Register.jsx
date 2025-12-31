// pages/Register.jsx
import React, { useEffect, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import anime from 'animejs/lib/anime.es.js';
import axios from 'axios';
import './Register.css';

const Register = () => {
  const formRef = useRef(null);
  const elementsRef = useRef([]);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [city, setCity] = useState('');
  const [occupation, setOccupation] = useState('');
  const [socialPlatform, setSocialPlatform] = useState('');
  const [socialUrl, setSocialUrl] = useState('');
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const nav = useNavigate();

  useEffect(() => {
    anime({
      targets: formRef.current,
      opacity: [0, 1],
      translateY: [50, 0],
      duration: 800,
      easing: 'easeOutExpo'
    });

    anime({
      targets: elementsRef.current,
      opacity: [0, 1],
      translateY: [20, 0],
      delay: anime.stagger(100, { start: 300 }),
      easing: 'easeOutExpo'
    });
  }, []);

  const addToElementsRef = (el) => {
    if (el && !elementsRef.current.includes(el)) {
      elementsRef.current.push(el);
    }
  };

  // Validation Functions
  const validateUsername = (value) => {
    if (!value.trim()) return 'Username is required';
    if (value.length < 3) return 'Username must be at least 3 characters';
    if (!/^[a-zA-Z0-9_-]+$/.test(value)) return 'Username can only contain letters, numbers, hyphens, and underscores';
    if (/^\d/.test(value)) return 'Username cannot start with a number';
    return '';
  };

  const validateEmail = (value) => {
    if (!value.trim()) return 'Email is required';
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) return 'Please enter a valid email address';
    return '';
  };

  const validatePassword = (value) => {
    if (!value) return 'Password is required';
    if (value.length < 6) return 'Password must be at least 6 characters';
    return '';
  };

  const validateConfirmPassword = (value) => {
    if (!value) return 'Please confirm your password';
    if (value !== password) return 'Passwords do not match';
    return '';
  };

  const validateCity = (value) => {
    if (value && !/^[a-zA-Z\s'-]+$/.test(value)) return 'City can only contain letters and hyphens';
    return '';
  };

  const validateOccupation = (value) => {
    if (value && !/^[a-zA-Z\s'-]+$/.test(value)) return 'Occupation can only contain letters and hyphens';
    return '';
  };

  const validateSocialPlatform = (value) => {
    if (value && !/^[a-zA-Z\s]+$/.test(value)) return 'Platform name should only contain letters';
    return '';
  };

  const validateSocialUrl = (value) => {
    if (value && !/^https?:\/\/.+/.test(value)) return 'Please enter a valid URL (starting with http:// or https://)';
    return '';
  };

  // Handle field changes with validation
  const handleUsernameChange = (e) => {
    const value = e.target.value;
    setUsername(value);
    if (value) {
      setErrors({ ...errors, username: validateUsername(value) });
    }
  };

  const handleEmailChange = (e) => {
    const value = e.target.value;
    setEmail(value);
    if (value) {
      setErrors({ ...errors, email: validateEmail(value) });
    }
  };

  const handlePasswordChange = (e) => {
    const value = e.target.value;
    setPassword(value);
    if (value) {
      setErrors({ ...errors, password: validatePassword(value) });
    }
  };

  const handleConfirmPasswordChange = (e) => {
    const value = e.target.value;
    setConfirmPassword(value);
    if (value) {
      setErrors({ ...errors, confirmPassword: validateConfirmPassword(value) });
    }
  };

  const handleCityChange = (e) => {
    const value = e.target.value;
    setCity(value);
    if (value) {
      setErrors({ ...errors, city: validateCity(value) });
    }
  };

  const handleOccupationChange = (e) => {
    const value = e.target.value;
    setOccupation(value);
    if (value) {
      setErrors({ ...errors, occupation: validateOccupation(value) });
    }
  };

  const handleSocialPlatformChange = (e) => {
    const value = e.target.value;
    setSocialPlatform(value);
    if (value) {
      setErrors({ ...errors, socialPlatform: validateSocialPlatform(value) });
    }
  };

  const handleSocialUrlChange = (e) => {
    const value = e.target.value;
    setSocialUrl(value);
    if (value) {
      setErrors({ ...errors, socialUrl: validateSocialUrl(value) });
    }
  };

  const validateAllFields = () => {
    const newErrors = {};

    newErrors.username = validateUsername(username);
    newErrors.email = validateEmail(email);
    newErrors.password = validatePassword(password);
    newErrors.confirmPassword = validateConfirmPassword(confirmPassword);
    
    if (city) newErrors.city = validateCity(city);
    if (occupation) newErrors.occupation = validateOccupation(occupation);
    if (socialPlatform) newErrors.socialPlatform = validateSocialPlatform(socialPlatform);
    if (socialUrl) newErrors.socialUrl = validateSocialUrl(socialUrl);

    setErrors(newErrors);

    return !Object.values(newErrors).some(error => error !== '');
  };

  const RegisterUser = async (e) => {
    e.preventDefault();

    if (!validateAllFields()) {
      return;
    }

    setLoading(true);

    try {
      const response = await axios.post(`http://127.0.0.1:8000/member/register`, {
        username,
        email,
        password,
        city: city || null,
        occupation: occupation || null,
        social_platform: socialPlatform || null,
        social_url: socialUrl || null
      });

      if (response.status === 201) {
        console.log('Member registered successfully');
        nav('/m_login');
      }
    } catch (error) {
      const errorMsg = error.response?.data?.detail ||
        error.response?.data?.message ||
        "Registration failed. Please try again.";
      setErrors({ submit: errorMsg });
      console.error('Registration error:', error.response?.data || error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-container" ref={formRef}>
        <div className="auth-header" ref={addToElementsRef}>
          <div className="header-icon">✓</div>
          <h2>Create Your Account</h2>
          <p>Join our verification community as a member</p>
        </div>

        {errors.submit && (
          <div className="error-banner" ref={addToElementsRef}>
            <span className="error-icon">⚠️</span>
            <span>{errors.submit}</span>
          </div>
        )}

        <form className="auth-form" onSubmit={RegisterUser}>
          {/* Required Fields Section */}
          <div className="form-section" ref={addToElementsRef}>
            <h3 className="section-title">Essential Information</h3>

            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="username">
                  Username <span className="required">*</span>
                </label>
                <div className="input-wrapper">
                  <input
                    type="text"
                    id="username"
                    placeholder="Choose a unique username"
                    value={username}
                    onChange={handleUsernameChange}
                    className={errors.username ? 'input-error' : ''}
                  />
                  {username && !errors.username && <span className="input-check">✓</span>}
                </div>
                {errors.username && <span className="error-message">{errors.username}</span>}
              </div>

              <div className="form-group">
                <label htmlFor="email">
                  Email <span className="required">*</span>
                </label>
                <div className="input-wrapper">
                  <input
                    type="email"
                    id="email"
                    placeholder="your.email@gmail.com"
                    value={email}
                    onChange={handleEmailChange}
                    className={errors.email ? 'input-error' : ''}
                  />
                  {email && !errors.email && <span className="input-check">✓</span>}
                </div>
                {errors.email && <span className="error-message">{errors.email}</span>}
              </div>

              <div className="form-group">
                <label htmlFor="password">
                  Password <span className="required">*</span>
                </label>
                <div className="input-wrapper">
                  <input
                    type="password"
                    id="password"
                    placeholder="At least 6 characters"
                    value={password}
                    onChange={handlePasswordChange}
                    className={errors.password ? 'input-error' : ''}
                  />
                  {password && !errors.password && <span className="input-check">✓</span>}
                </div>
                {errors.password && <span className="error-message">{errors.password}</span>}
              </div>

              <div className="form-group">
                <label htmlFor="confirmPassword">
                  Confirm Password <span className="required">*</span>
                </label>
                <div className="input-wrapper">
                  <input
                    type="password"
                    id="confirmPassword"
                    placeholder="Re-enter your password"
                    value={confirmPassword}
                    onChange={handleConfirmPasswordChange}
                    className={errors.confirmPassword ? 'input-error' : ''}
                  />
                  {confirmPassword && !errors.confirmPassword && <span className="input-check">✓</span>}
                </div>
                {errors.confirmPassword && <span className="error-message">{errors.confirmPassword}</span>}
              </div>
            </div>
          </div>

          {/* Optional Profile Information Section */}
          <div className="form-section" ref={addToElementsRef}>
            <h3 className="section-title">Profile Information (Optional)</h3>

            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="city">City</label>
                <div className="input-wrapper">
                  <input
                    type="text"
                    id="city"
                    placeholder="e.g., Karachi, Lahore"
                    value={city}
                    onChange={handleCityChange}
                    className={errors.city ? 'input-error' : ''}
                  />
                  {city && !errors.city && <span className="input-check">✓</span>}
                </div>
                {errors.city && <span className="error-message">{errors.city}</span>}
              </div>

              <div className="form-group">
                <label htmlFor="occupation">Occupation</label>
                <div className="input-wrapper">
                  <input
                    type="text"
                    id="occupation"
                    placeholder="e.g., Software Engineer"
                    value={occupation}
                    onChange={handleOccupationChange}
                    className={errors.occupation ? 'input-error' : ''}
                  />
                  {occupation && !errors.occupation && <span className="input-check">✓</span>}
                </div>
                {errors.occupation && <span className="error-message">{errors.occupation}</span>}
              </div>

              <div className="form-group">
                <label htmlFor="socialPlatform">Social Platform</label>
                <div className="input-wrapper">
                  <input
                    type="text"
                    id="socialPlatform"
                    placeholder="e.g., Twitter, LinkedIn"
                    value={socialPlatform}
                    onChange={handleSocialPlatformChange}
                    className={errors.socialPlatform ? 'input-error' : ''}
                  />
                  {socialPlatform && !errors.socialPlatform && <span className="input-check">✓</span>}
                </div>
                {errors.socialPlatform && <span className="error-message">{errors.socialPlatform}</span>}
              </div>

              <div className="form-group">
                <label htmlFor="socialUrl">Social Profile URL</label>
                <div className="input-wrapper">
                  <input
                    type="url"
                    id="socialUrl"
                    placeholder="https://twitter.com/yourprofile"
                    value={socialUrl}
                    onChange={handleSocialUrlChange}
                    className={errors.socialUrl ? 'input-error' : ''}
                  />
                  {socialUrl && !errors.socialUrl && <span className="input-check">✓</span>}
                </div>
                {errors.socialUrl && <span className="error-message">{errors.socialUrl}</span>}
              </div>
            </div>
          </div>

          <div className="form-action" ref={addToElementsRef}>
            <button 
              type="submit" 
              className="btn btn-primary"
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="spinner"></span>
                  Registering...
                </>
              ) : (
                'Register as Member'
              )}
            </button>
          </div>
        </form>

        <div className="auth-footer" ref={addToElementsRef}>
          <p>
            Already have an account? <Link to="/m_login">Sign in here</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;