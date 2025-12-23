/**
 * Main entry point for Visual AutoView frontend
 */

import './app';
import { initializeAuthHandler } from './services/auth-handler';

// Initialize authentication handler first
initializeAuthHandler();

// Initialize the application
const app = document.getElementById('app');

if (app) {
  // Remove loading container
  app.innerHTML = '';

  // Create and mount the main app component
  const vavApp = document.createElement('vav-app');
  app.appendChild(vavApp);

  console.log('Visual AutoView initialized');
}

// Hot module replacement for development
if (import.meta.hot) {
  import.meta.hot.accept();
}
