// Dashboard Page component
import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import { parkingService } from '../services/parkingService';
import './Pages.css';

function DashboardPage({ user }) {
  const [currentAssignment, setCurrentAssignment] = useState(null);
  const [explanation, setExplanation] = useState('');
  const [unreadNotifications, setUnreadNotifications] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCurrentAssignment();
    fetchUnreadNotifications();
    
    // Auto-refresh unread notifications every 5 seconds
    const interval = setInterval(() => {
      fetchUnreadNotifications();
    }, 5000);
    
    // Cleanup interval on unmount
    return () => clearInterval(interval);
  }, []);

  const fetchCurrentAssignment = async () => {
    try {
      const data = await parkingService.getCurrentAssignment();
      setCurrentAssignment(data);
      
      // Get assignment explanation
      if (data.id) {
        const exp = await parkingService.getAssignmentExplanation(data.id);
        setExplanation(exp.explanation);
      }
    } catch (error) {
      // No current assignment
      setCurrentAssignment(null);
    } finally {
      setLoading(false);
    }
  };

  const fetchUnreadNotifications = async () => {
    try {
      const data = await parkingService.getUnreadNotifications();
      setUnreadNotifications(data.length || 0);
    } catch (error) {
      console.error('Error fetching notifications:', error);
    }
  };

  if (loading) {
    return <main className="container"><p>Loading...</p></main>;
  }

  return (
    <main className="container">
      <div className="dashboard">
        <h1>Welcome, {user?.first_name || user?.username}!</h1>

        <div className="dashboard-grid">
          {/* Current Assignment Card */}
          <div className="card">
            <h2>🅿️ Current Parking Assignment</h2>
            {currentAssignment ? (
              <>
                <div className="assignment-info">
                  <div className="info-row">
                    <strong>Slot:</strong>
                    <span>{currentAssignment.parking_slot_info.slot_number}</span>
                  </div>
                  <div className="info-row">
                    <strong>Location:</strong>
                    <span>{currentAssignment.parking_slot_info.lot_name}</span>
                  </div>
                  <div className="info-row">
                    <strong>Type:</strong>
                    <span className="badge badge-info">
                      {currentAssignment.parking_slot_info.slot_type}
                    </span>
                  </div>
                  <div className="info-row">
                    <strong>Duration:</strong>
                    <span>
                      {new Date(currentAssignment.start_datetime).toLocaleString()} to{' '}
                      {new Date(currentAssignment.end_datetime).toLocaleString()}
                    </span>
                  </div>
                  <div className="info-row">
                    <strong>Distance:</strong>
                    <span>{Math.round(currentAssignment.distance_to_building)}m</span>
                  </div>
                  <div className="info-row">
                    <strong>AI Confidence:</strong>
                    <span>
                      <div className="confidence-bar">
                        <div
                          className="confidence-fill"
                          style={{
                            width: `${currentAssignment.ai_confidence_score * 100}%`,
                          }}
                        />
                      </div>
                      {Math.round(currentAssignment.ai_confidence_score * 100)}%
                    </span>
                  </div>
                </div>
                <div className="explanation">
                  <h4>Why This Slot?</h4>
                  <p>{explanation}</p>
                </div>
              </>
            ) : (
              <p>No active parking assignment. Create a schedule to get assigned a parking slot!</p>
            )}
          </div>

          {/* Quick Stats */}
          <div className="card">
            <h2>📊 Quick Stats</h2>
            <div className="stats">
              <div className="stat">
                <span className="stat-number">{unreadNotifications}</span>
                <span className="stat-label">Unread Notifications</span>
              </div>
              <div className="stat">
                <span className="stat-number">{user?.user_type === 'student' ? 'Student' : 'Employee'}</span>
                <span className="stat-label">Account Type</span>
              </div>
              <div className="stat">
                <span className="stat-number" id="vehicle-display">
                  {user?.vehicle_plate || 'Not set'}
                </span>
                <span className="stat-label">Vehicle Plate</span>
              </div>
            </div>
          </div>

          {/* Next Steps */}
          <div className="card full-width">
            <h2>📋 Next Steps</h2>
            <div className="steps">
              <div className="step">
                <span className="step-number">1</span>
                <h4>Add Your Schedule</h4>
                <p>Upload your class or work schedule to get automatic parking assignments</p>
              </div>
              <div className="step">
                <span className="step-number">2</span>
                <h4>View Assignments</h4>
                <p>Check your parking slots and get directions to your assigned spots</p>
              </div>
              <div className="step">
                <span className="step-number">3</span>
                <h4>Upgrade Subscription</h4>
                <p>Get priority parking with Premium or VIP subscription plans</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}

export default DashboardPage;
