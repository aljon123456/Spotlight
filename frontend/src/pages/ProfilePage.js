// Profile Page component
import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import { authService } from '../services/authService';
import './Pages.css';

function ProfilePage({ user, setUser }) {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone_number: '',
    vehicle_plate: '',
    vehicle_type: '',
    profile_picture: null,
  });
  const [loading, setLoading] = useState(false);
  const [previewImage, setPreviewImage] = useState(null);
  const [subscription, setSubscription] = useState(null);

  useEffect(() => {
    if (user) {
      setFormData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        email: user.email || '',
        phone_number: user.phone_number || '',
        vehicle_plate: user.vehicle_plate || '',
        vehicle_type: user.vehicle_type || '',
        profile_picture: null,
      });
      
      // Fetch subscription info
      fetchSubscription();
    }
  }, [user]);

  const fetchSubscription = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/subscription/current/', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      const data = await response.json();
      setSubscription(data);
    } catch (error) {
      console.error('Error fetching subscription:', error);
    }
  };

  const handleChange = (e) => {
    const { name, value, files } = e.target;
    if (files) {
      setFormData({
        ...formData,
        [name]: files[0],
      });
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewImage(reader.result);
      };
      reader.readAsDataURL(files[0]);
    } else {
      setFormData({
        ...formData,
        [name]: value,
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      let result;
      
      // If there's a profile picture, create FormData
      if (formData.profile_picture) {
        const data = new FormData();
        data.append('first_name', formData.first_name);
        data.append('last_name', formData.last_name);
        data.append('email', formData.email);
        data.append('phone_number', formData.phone_number);
        data.append('vehicle_plate', formData.vehicle_plate);
        data.append('vehicle_type', formData.vehicle_type);
        data.append('profile_picture', formData.profile_picture);
        
        // Manual upload for FormData
        const response = await fetch('http://localhost:8000/api/auth/profile/', {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          },
          body: data,
        });
        if (!response.ok) throw new Error('Update failed');
        result = await response.json();
      } else {
        const updateData = {
          first_name: formData.first_name,
          last_name: formData.last_name,
          email: formData.email,
          phone_number: formData.phone_number,
          vehicle_plate: formData.vehicle_plate,
          vehicle_type: formData.vehicle_type,
        };
        result = await authService.updateProfile(updateData);
      }

      // Update user state with result
      setUser(result);
      
      // Save updated user to localStorage for persistence
      localStorage.setItem('user_data', JSON.stringify(result));
      
      // Reset preview image after successful upload
      setPreviewImage(null);
      
      toast.success('Profile updated successfully!');
    } catch (error) {
      console.error('Profile update error:', error);
      toast.error(error?.message || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="container">
      <h1>👤 User Profile</h1>

      {/* Account Type Badge - PROMINENT */}
      <div className="account-type-badge">
        <p className="account-label">Account Type:</p>
        <h2 className={`account-type ${user?.user_type}`}>
          {user?.user_type === 'student' ? '🎓 STUDENT' : '💼 EMPLOYEE'}
        </h2>
        <p className="account-description">
          {user?.user_type === 'student' 
            ? 'Student - Access smart parking for classes and campus activities'
            : 'Employee - Access smart parking for work and office hours'
          }
        </p>
      </div>

      {/* Subscription Status Badge */}
      {subscription && (
        <div className="subscription-badge">
          <p className="subscription-label">Current Subscription:</p>
          <h2 className={`subscription-type ${subscription?.subscription_type}`}>
            {subscription?.subscription_type ? subscription.subscription_type.toUpperCase() : 'NONE'}
          </h2>
          {subscription?.subscription_type && subscription?.status === 'active' && (
            <>
              <p className="subscription-status">✅ Active</p>
              {subscription?.end_date && (
                <p className="subscription-expiry">
                  Expires: {new Date(subscription.end_date).toLocaleDateString()}
                </p>
              )}
            </>
          )}
        </div>
      )}

      <div className="card">
        <form onSubmit={handleSubmit}>
          {/* Profile Picture */}
          <div className="form-group profile-picture-group">
            <label>Profile Picture</label>
            <div className="profile-picture-preview">
              {previewImage ? (
                <img src={previewImage} alt="Preview" />
              ) : user?.profile_picture ? (
                <img src={user.profile_picture} alt="Profile" />
              ) : (
                <div className="placeholder">No image</div>
              )}
            </div>
            <input
              type="file"
              name="profile_picture"
              onChange={handleChange}
              accept="image/*"
            />
          </div>

          {/* Name Fields */}
          <div className="form-row">
            <div className="form-group half">
              <label htmlFor="first_name">First Name</label>
              <input
                type="text"
                id="first_name"
                name="first_name"
                value={formData.first_name}
                onChange={handleChange}
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
              />
            </div>
          </div>

          {/* Email */}
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
            />
          </div>

          {/* Phone */}
          <div className="form-group">
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

          {/* Vehicle Info */}
          <div className="form-row">
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
            <div className="form-group half">
              <label htmlFor="vehicle_type">Vehicle Type</label>
              <input
                type="text"
                id="vehicle_type"
                name="vehicle_type"
                value={formData.vehicle_type}
                onChange={handleChange}
                placeholder="e.g., Honda Civic"
              />
            </div>
          </div>

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Saving...' : 'Save Changes'}
          </button>
        </form>
      </div>
    </main>
  );
}

export default ProfilePage;
