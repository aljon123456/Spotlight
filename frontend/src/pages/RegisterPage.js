// Register Page component
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { toast } from 'react-toastify';
import { authService } from '../services/authService';
import './AuthPages.css';

function RegisterPage({ setUser }) {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirm_password: '',
    first_name: '',
    last_name: '',
    user_type: 'student',
    phone_number: '',
    vehicle_plate: '',
  });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    if (formData.password !== formData.confirm_password) {
      toast.error('Passwords do not match!');
      setLoading(false);
      return;
    }

    try {
      const response = await authService.register(formData);
      const userData = response.user;
      setUser(userData);
      // Save user data to localStorage for persistence
      localStorage.setItem('user_data', JSON.stringify(userData));
      toast.success('Registration successful! Welcome to SpotLight.');
      navigate('/dashboard');
    } catch (error) {
      const errorMsg = error.username?.[0] || error.email?.[0] || 'Registration failed. Please try again.';
      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1>🚗 SpotLight</h1>
        <h2>Create Account</h2>
        <p className="subtitle">Join our smart parking system</p>

        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group half">
              <label htmlFor="first_name">First Name</label>
              <input
                type="text"
                id="first_name"
                name="first_name"
                value={formData.first_name}
                onChange={handleChange}
                placeholder="First name"
                required
              />
            </div>
            <div className="form-group half">
              <label htmlFor="last_name">Last Name</label>
              <input
                type="text"
                id="last_name"
                name="last_name"
                value={formData.last_name}
                onChange={handleChange}
                placeholder="Last name"
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="Choose a username"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="your.email@university.edu"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="user_type">User Type</label>
            <select
              id="user_type"
              name="user_type"
              value={formData.user_type}
              onChange={handleChange}
            >
              <option value="student">Student</option>
              <option value="employee">Employee</option>
            </select>
          </div>

          <div className="form-row">
            <div className="form-group half">
              <label htmlFor="password">Password</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="At least 8 characters"
                required
              />
            </div>
            <div className="form-group half">
              <label htmlFor="confirm_password">Confirm Password</label>
              <input
                type="password"
                id="confirm_password"
                name="confirm_password"
                value={formData.confirm_password}
                onChange={handleChange}
                placeholder="Confirm password"
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group half">
              <label htmlFor="phone_number">Phone Number</label>
              <input
                type="tel"
                id="phone_number"
                name="phone_number"
                value={formData.phone_number}
                onChange={handleChange}
                placeholder="+1-555-0000"
              />
            </div>
            <div className="form-group half">
              <label htmlFor="vehicle_plate">Vehicle Plate</label>
              <input
                type="text"
                id="vehicle_plate"
                name="vehicle_plate"
                value={formData.vehicle_plate}
                onChange={handleChange}
                placeholder="ABC 1234"
              />
            </div>
          </div>

          <button type="submit" className="btn-primary submit-btn" disabled={loading}>
            {loading ? 'Creating Account...' : 'Register'}
          </button>
        </form>

        <p className="auth-footer">
          Already have an account? <Link to="/login">Login here</Link>
        </p>
      </div>
    </div>
  );
}

export default RegisterPage;
