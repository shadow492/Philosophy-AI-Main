import axios from 'axios';

const API_URL = '/api';

// Authentication API calls
export const loginUser = (username, password) => {
  return axios.post(`${API_URL}/auth/login/`, { username, password });
};

export const registerUser = (userData) => {
  return axios.post(`${API_URL}/auth/register/`, userData);
};

// Philosophers API calls
export const getPhilosophers = () => {
  return axios.get(`${API_URL}/philosophers/`);
};

export const getPhilosopher = (id) => {
  return axios.get(`${API_URL}/philosophers/${id}/`);
};

// Chat sessions API calls
export const getChatSessions = () => {
  return axios.get(`${API_URL}/sessions/`);
};

export const createChatSession = (philosopher) => {
  return axios.post(`${API_URL}/sessions/create_session/`, { philosopher });
};

export const getChatSession = (id) => {
  return axios.get(`${API_URL}/sessions/${id}/`);
};

export const sendMessage = (sessionId, message) => {
  return axios.post(`${API_URL}/sessions/${sessionId}/add_message/`, { message });
};

export const changePhilosopher = (sessionId, philosopher) => {
  return axios.patch(`${API_URL}/sessions/${sessionId}/change-philosopher/`, { philosopher });
};