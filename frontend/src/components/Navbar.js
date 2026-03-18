// Navbar component - Main navigation
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../services/authService';
import './Navbar.css';

function Navbar({ user }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const navigate = useNavigate();

  const handleLogout = () => {
    authService.logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/dashboard" className="navbar-logo">
          🚗 SpotLight
        </Link>

        <button
          className="menu-toggle"
          onClick={() => setMenuOpen(!menuOpen)}
        >
          ☰
        </button>

        <div className={`nav-menu ${menuOpen ? 'active' : ''}`}>
          <Link to="/dashboard" className="nav-link">
            Dashboard
          </Link>
          <Link to="/schedules" className="nav-link">
            Schedules
          </Link>
          <Link to="/assignments" className="nav-link">
            Assignments
          </Link>
          <Link to="/notifications" className="nav-link">
            Notifications
          </Link>
          <Link to="/profile" className="nav-link">
            Profile
          </Link>
          <Link to="/subscription" className="nav-link subscription-link">
            💳 Subscription
          </Link>
        </div>

        <div className="navbar-user">
          <div className="user-info">
            <span className="user-name">{user?.first_name || user?.username}</span>
            <span className={`user-type ${user?.user_type}`}>
              {user?.user_type === 'student' ? '🎓 Student' : '💼 Employee'}
            </span>
          </div>
          <button onClick={handleLogout} className="logout-btn">
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
