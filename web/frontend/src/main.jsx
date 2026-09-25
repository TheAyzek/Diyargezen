import React from 'react'
import ReactDOM from 'react-dom/client'
import axios from 'axios'
import App from './App.jsx'
import './index.css'
import './theme.css'
import { installSessionInterceptors } from './utils/httpSession.js'

// Configure Axios default base URL for desktop / file:// / web environments
if (typeof window !== 'undefined') {
  const origin = window.location.origin || '';
  if (origin.startsWith('file:') || origin.startsWith('app:') || origin.includes('qtwebengine')) {
    axios.defaults.baseURL = 'http://127.0.0.1:8000';
  } else {
    axios.defaults.baseURL = '';
  }
}

installSessionInterceptors(axios, () => {
  window.dispatchEvent(new Event('diyargezen-session-expired'));
});


ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)

