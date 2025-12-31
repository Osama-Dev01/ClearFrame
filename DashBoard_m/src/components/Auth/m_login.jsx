import React, { useEffect, useState, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import anime from 'animejs';
import { useMember } from './MemberContext';
import './m_login.css';

const MemberLogin = () => {
  const formRef = useRef(null);
  const elementsRef = useRef([]);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const nav = useNavigate();
  const { loginMember } = useMember();

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

  const validateEmail = (value) => {
    if (!value.trim()) return 'Email is required';
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) return 'Please enter a valid email address';
    return '';
  };

  const validatePassword = (value) => {
    if (!value) return 'Password is required';
    return '';
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

  const validateAllFields = () => {
    const newErrors = {};
    newErrors.email = validateEmail(email);
    newErrors.password = validatePassword(password);
    
    setErrors(newErrors);
    return !Object.values(newErrors).some(error => error !== '');
  };

  const handleLogin = async (e) => {
    e.preventDefault();

    if (!validateAllFields()) {
      return;
    }

    setLoading(true);

    try {
      const response = await axios.post('http://127.0.0.1:8000/member/login', {
        email,
        password
      });

      const token = response.data.token;
      const memberData = {
        id: response.data.id
        // You can add more fields later if backend includes them
      };

      loginMember(memberData, token);
      nav('/member'); // Redirect to member dashboard
      
    } catch (error) {
      const errorMsg = error.response?.status === 401 
        ? 'Invalid email or password' 
        : 'Login failed. Please try again.';
      setErrors({ submit: errorMsg });
      console.error('Login error:', error.response?.data || error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-container" ref={formRef}>
        <div className="auth-header">
          <div className="header-icon">🔐</div>
          <h2 ref={addToElementsRef}>Member Login</h2>
          <p ref={addToElementsRef}>Sign in to access your verification dashboard</p>
        </div>

        {errors.submit && (
          <div className="error-banner" ref={addToElementsRef}>
            <span className="error-icon">⚠️</span>
            <span>{errors.submit}</span>
          </div>
        )}

        <form className="auth-form" onSubmit={handleLogin}>
          <div className="form-group" ref={addToElementsRef}>
            <label htmlFor="email">Email</label>
            <div className="input-wrapper">
              <input
                type="email"
                id="email"
                placeholder="your.email@example.com"
                value={email}
                onChange={handleEmailChange}
                className={errors.email ? 'input-error' : ''}
              />
              {email && !errors.email && <span className="input-check">✓</span>}
            </div>
            {errors.email && <span className="error-message">{errors.email}</span>}
          </div>

          <div className="form-group" ref={addToElementsRef}>
            <label htmlFor="password">Password</label>
            <div className="input-wrapper">
              <input
                type="password"
                id="password"
                placeholder="Enter your password"
                value={password}
                onChange={handlePasswordChange}
                className={errors.password ? 'input-error' : ''}
              />
              {password && !errors.password && <span className="input-check">✓</span>}
            </div>
            {errors.password && <span className="error-message">{errors.password}</span>}
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
                  Signing In...
                </>
              ) : (
                'Sign In'
              )}
            </button>
          </div>

          <div className="register-link" ref={addToElementsRef}>
            <p>
              Don't have an account? <Link to="/register">Register here</Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
};

export default MemberLogin;