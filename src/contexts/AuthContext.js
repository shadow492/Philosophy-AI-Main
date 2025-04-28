import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext(null);

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);
  
  // Check if user is authenticated on initial load
  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('token');
      const storedUser = localStorage.getItem('user');
      
      if (storedToken && storedUser) {
        setToken(storedToken);
        setUser(JSON.parse(storedUser));
        axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
      }
      
      setLoading(false);
    };
    
    initAuth();
  }, []);
  
  // Set axios default authorization header when token changes
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }
  }, [token]);
  
  // Login function
  const login = async (username, password) => {
    try {
      const response = await axios.post('/api/auth/login/', { username, password });
      const { access, user: userData } = response.data;
      
      setToken(access);
      setUser(userData);
      
      localStorage.setItem('token', access);
      localStorage.setItem('user', JSON.stringify(userData));
      
      return { success: true };
    } catch (error) {
      console.error('Login error:', error);
      
      let errorMessage = 'Login failed. Please try again.';
      if (error.response) {
        // Extract error message from response
        const responseData = error.response.data;
        if (responseData.detail) {
          errorMessage = responseData.detail;
        } else if (responseData.non_field_errors) {
          errorMessage = responseData.non_field_errors[0];
        } else if (typeof responseData === 'string') {
          errorMessage = responseData;
        }
      }
      
      return { success: false, message: errorMessage };
    }
  };
  
  // Register function
  const register = async (userData) => {
    try {
      const response = await axios.post('/api/auth/register/', {
        username: userData.username,
        email: userData.email,
        password: userData.password,
        password2: userData.password2
      });
      
      const { access, user: newUser } = response.data;
      
      setToken(access);
      setUser(newUser);
      
      localStorage.setItem('token', access);
      localStorage.setItem('user', JSON.stringify(newUser));
      
      return { success: true };
    } catch (error) {
      console.error('Registration error:', error);
      
      let errorMessage = 'Registration failed. Please try again.';
      if (error.response) {
        // Extract error message from response
        const responseData = error.response.data;
        if (responseData.detail) {
          errorMessage = responseData.detail;
        } else if (responseData.username) {
          errorMessage = `Username: ${responseData.username[0]}`;
        } else if (responseData.email) {
          errorMessage = `Email: ${responseData.email[0]}`;
        } else if (responseData.password) {
          errorMessage = `Password: ${responseData.password[0]}`;
        } else if (typeof responseData === 'string') {
          errorMessage = responseData;
        }
      }
      
      return { success: false, message: errorMessage };
    }
  };
  
  // Logout function
  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  };
  
  const isAuthenticated = !!token;
  
  const value = {
    user,
    token,
    isAuthenticated,
    loading,
    login,
    register,
    logout
  };
  
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};