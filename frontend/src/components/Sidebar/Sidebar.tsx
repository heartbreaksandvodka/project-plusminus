import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import './Sidebar.css';

const Sidebar: React.FC = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const toggleSidebar = () => {
    setIsCollapsed(!isCollapsed);
  };

  const toggleMobileSidebar = () => {
    setIsMobileOpen(!isMobileOpen);
  };

  const menuItems = [
    {
      icon: '🏠',
      label: 'Dashboard',
      path: '/dashboard',
      active: location.pathname === '/dashboard'
    },
    {
      icon: '👤',
      label: 'Profile',
      path: '/profile',
      active: location.pathname === '/profile'
    },
    {
      icon: '📝',
      label: 'Update Profile',
      path: '/update-profile',
      active: location.pathname === '/update-profile'
    },
    {
      icon: '🔒',
      label: 'Change Password',
      path: '/change-password',
      active: location.pathname === '/change-password'
    },
    {
      icon: '🧮',
      label: 'Algorithms',
      path: '/algorithms',
      active: location.pathname === '/algorithms'
    },
    {
      icon: '💳',
      label: 'Subscriptions',
      path: '/subscriptions',
      active: location.pathname === '/subscriptions'
    },
    {
      icon: '⚙️',
      label: 'Settings',
      path: '/settings',
      active: location.pathname === '/settings'
    }
  ];

  return (
    <>
      {/* Mobile Menu Button */}
      <button 
        className="mobile-menu-button"
        onClick={toggleMobileSidebar}
        aria-label="Toggle mobile menu"
      >
        ☰
      </button>

      {/* Mobile Overlay */}
      {isMobileOpen && (
        <div 
          className="mobile-overlay"
          onClick={toggleMobileSidebar}
        />
      )}

      {/* Sidebar */}
      <aside className={`sidebar ${isCollapsed ? 'collapsed' : ''} ${isMobileOpen ? 'mobile-open' : ''}`}>
        {/* Sidebar Header */}
        <div className="sidebar-header">
          <div className="logo">
            <span className="logo-icon">⚡</span>
            {!isCollapsed && <span className="logo-text">PlusMinus</span>}
          </div>
          <button 
            className="collapse-btn"
            onClick={toggleSidebar}
            aria-label="Toggle sidebar"
          >
            {isCollapsed ? '→' : '←'}
          </button>
        </div>

        {/* User Info */}
        <div className="user-info">
          <div className="user-avatar">
            <span>{user?.first_name?.charAt(0) || 'U'}</span>
          </div>
          {!isCollapsed && (
            <div className="user-details">
              <div className="user-name">{user?.first_name} {user?.last_name}</div>
              <div className="user-email">{user?.email}</div>
            </div>
          )}
        </div>

        {/* Navigation Menu */}
        <nav className="sidebar-nav">
          <ul className="nav-list">
            {menuItems.map((item) => (
              <li key={item.path} className="nav-item">
                <Link
                  to={item.path}
                  className={`nav-link ${item.active ? 'active' : ''}`}
                  onClick={() => setIsMobileOpen(false)}
                  title={isCollapsed ? item.label : ''}
                >
                  <span className="nav-icon">{item.icon}</span>
                  {!isCollapsed && <span className="nav-label">{item.label}</span>}
                </Link>
              </li>
            ))}
          </ul>
        </nav>

        {/* Sidebar Footer */}
        <div className="sidebar-footer">
          <button 
            className="logout-btn"
            onClick={handleLogout}
            title={isCollapsed ? 'Logout' : ''}
          >
            <span className="logout-icon">🚪</span>
            {!isCollapsed && <span className="logout-text">Logout</span>}
          </button>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
