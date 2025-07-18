import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { LoginCredentials } from '../types/auth';

const Login: React.FC = () => {
  const location = useLocation();
  const [credentials, setCredentials] = useState<LoginCredentials>({
    email: location.state?.email || '',
    password: '',
  });
  const [error, setError] = useState(location.state?.message || '');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await login(credentials);
      
      // Handle remember me functionality
      if (rememberMe) {
        localStorage.setItem('rememberMe', 'true');
        localStorage.setItem('savedEmail', credentials.email);
      } else {
        localStorage.removeItem('rememberMe');
        localStorage.removeItem('savedEmail');
      }
      
      navigate('/dashboard');
    } catch (err: any) {
      const errorData = err.response?.data;
      
      if (errorData?.error_type === 'user_not_found') {
        // User doesn't exist, redirect to register
        setError(errorData.message);
        setTimeout(() => {
          navigate('/register', { 
            state: { 
              email: credentials.email,
              message: 'No account found with this email. Please register first.' 
            }
          });
        }, 2000);
      } else if (errorData?.error_type === 'incorrect_password') {
        // Wrong password
        setError(errorData.message);
      } else if (errorData?.error_type === 'inactive_user') {
        // Account deactivated
        setError(errorData.message);
      } else {
        // Generic error
        setError(errorData?.message || 'Login failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setCredentials(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  // Load saved email on component mount
  React.useEffect(() => {
    const savedEmail = localStorage.getItem('savedEmail');
    const isRemembered = localStorage.getItem('rememberMe') === 'true';
    
    if (isRemembered && savedEmail && !location.state?.email) {
      setCredentials(prev => ({ ...prev, email: savedEmail }));
      setRememberMe(true);
    }
    
    // Clear the redirect message after 5 seconds
    if (location.state?.message) {
      const timer = setTimeout(() => {
        setError('');
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [location.state]);

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Login</h2>
        <form onSubmit={handleSubmit} className="auth-form">
          {error && <div className="error-message">{error}</div>}
          
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              value={credentials.email}
              onChange={handleChange}
              required
              placeholder="Enter your email"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <div className="password-input-container">
              <input
                type={showPassword ? "text" : "password"}
                id="password"
                name="password"
                value={credentials.password}
                onChange={handleChange}
                required
                placeholder="Enter your password"
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword(!showPassword)}
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? "👁️" : "🙈"}
              </button>
            </div>
          </div>

          <div className="form-group remember-me">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
              />
              <span className="checkmark"></span>
              Remember me
            </label>
          </div>

          <button type="submit" disabled={loading} className="auth-button">
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <div className="forgot-password-link">
          <p><Link to="/forgot-password">Forgot your password?</Link></p>
        </div>

        <div className="auth-link">
          <p>Don't have an account? <Link to="/register">Register here</Link></p>
        </div>
      </div>
    </div>
  );
};

export default Login;
