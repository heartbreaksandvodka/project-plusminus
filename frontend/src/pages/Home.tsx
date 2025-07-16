import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Home: React.FC = () => {
  const { isAuthenticated, user } = useAuth();

  return (
    <div className="home-container">
      <header className="home-header">
        <h1>Welcome to Auth App</h1>
        <p>A full-stack authentication system with Django and React</p>
      </header>

      <main className="home-content">
        {isAuthenticated ? (
          <div className="authenticated-content">
            <h2>Welcome back, {user?.first_name}!</h2>
            <p>You are successfully logged in.</p>
            <div className="home-actions">
              <Link to="/dashboard" className="home-button primary">
                Go to Dashboard
              </Link>
            </div>
          </div>
        ) : (
          <div className="unauthenticated-content">
            <h2>Get Started</h2>
            <p>Please login or register to access your dashboard.</p>
            <div className="home-actions">
              <Link to="/login" className="home-button primary">
                Login
              </Link>
              <Link to="/register" className="home-button secondary">
                Register
              </Link>
            </div>
          </div>
        )}

        <div className="features">
          <h3>Features</h3>
          <ul>
            <li>✅ JWT Authentication</li>
            <li>✅ User Registration & Login</li>
            <li>✅ Protected Routes</li>
            <li>✅ Token Refresh</li>
            <li>✅ User Dashboard</li>
            <li>✅ Modern UI</li>
          </ul>
        </div>
      </main>
    </div>
  );
};

export default Home;
