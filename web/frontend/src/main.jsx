import React from 'react'
import ReactDOM from 'react-dom/client'
import axios from 'axios'
import App from './App.jsx'
import './index.css'

// Configure Axios default base URL for desktop / file:// / web environments
if (typeof window !== 'undefined') {
  const origin = window.location.origin || '';
  if (origin.startsWith('file:') || origin.startsWith('app:') || origin.includes('qtwebengine')) {
    axios.defaults.baseURL = 'http://127.0.0.1:8000';
  } else {
    axios.defaults.baseURL = '';
  }
}

// Configure Axios request interceptor for JWT Auth
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, error => {
  return Promise.reject(error);
});

// Configure Axios response interceptor to handle unauthorized access cleanly without reloading
axios.interceptors.response.use(response => response, error => {
  if (error.response && error.response.status === 401) {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
  }
  return Promise.reject(error);
});


ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)

