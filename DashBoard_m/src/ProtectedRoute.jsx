import React, { useEffect, useState } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import Cookies from 'js-cookie';
import axios from 'axios';


const ProtectedRoute = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(null); // null = loading

  useEffect(() => {
    const verifyToken = async () => {
      const token = Cookies.get('token');

      if (!token) {
        setIsAuthenticated(false);
        return;
      }

      try {
        const response = await axios.post(`${process.env.REACT_APP_API}checkme`, {}, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (response.status === 200) {
          setIsAuthenticated(true);
        }
      } catch (error) {
        setIsAuthenticated(false);
        console.error("Token check failed:", error);
      }
    };

    verifyToken();
  }, []);

  if (isAuthenticated === null) {
    // While checking token
    return <div>Loading...</div>;
  }

  return isAuthenticated ? <Outlet /> : <Navigate to="/login" />;
};

export default ProtectedRoute;
