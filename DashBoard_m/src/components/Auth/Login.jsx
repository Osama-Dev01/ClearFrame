import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import anime from 'animejs';
import './Auth.css';
import { Shield } from "lucide-react";

const Login = () => {
  const formRef = useRef(null);
  const elementsRef = useRef([]);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
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

  const validateUsername = (value) => {
    if (!value.trim()) return 'Username is required';
    return '';
  };

  const validatePassword = (value) => {
    if (!value) return 'Password is required';
    return '';
  };

  const handleUsernameChange = (e) => {
    const value = e.target.value;
    setUsername(value);
    if (value) {
      setErrors({ ...errors, username: validateUsername(value) });
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
    newErrors.username = validateUsername(username);
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
      await axios.post(`http://127.0.0.1:8000/admin/login`, { 
        username, 
        password 
      });
      
      // On successful login, redirect to dashboard
      nav('/');
      
    } catch (error) {
      const errorMsg = error.response?.status === 401 
        ? 'Invalid admin credentials' 
        : 'Login failed. Please try again.';
      setErrors({ submit: errorMsg });
      console.error('Admin login error:', error.response?.data || error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-container" ref={formRef}>
        <div className="auth-header">
         <div className="header-icon">
  <Shield className="w-5 h-5 text-purple-600" />
</div>
          <h2 ref={addToElementsRef}>Admin Login</h2>
          <p ref={addToElementsRef}>Sign in to access admin dashboard</p>
        </div>

        {errors.submit && (
          <div className="error-banner" ref={addToElementsRef}>
            <span className="error-icon">⚠️</span>
            <span>{errors.submit}</span>
          </div>
        )}

        <form className="auth-form" onSubmit={handleLogin}>
          <div className="form-group" ref={addToElementsRef}>
            <label htmlFor="username">Username</label>
            <div className="input-wrapper">
              <input 
                type="text" 
                id="username" 
                placeholder="Enter admin username" 
                value={username}
                onChange={handleUsernameChange}
                className={errors.username ? 'input-error' : ''}
              />
              {username && !errors.username && <span className="input-check">✓</span>}
            </div>
            {errors.username && <span className="error-message">{errors.username}</span>}
          </div>

          <div className="form-group" ref={addToElementsRef}>
            <label htmlFor="password">Password</label>
            <div className="input-wrapper">
              <input 
                type="password" 
                id="password" 
                placeholder="Enter admin password" 
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
                'Admin Login'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Login;