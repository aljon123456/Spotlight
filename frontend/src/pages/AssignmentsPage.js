// Assignments Page component
import React, { useState, useEffect } from 'react';
import { parkingService } from '../services/parkingService';
import './Pages.css';

function AssignmentsPage() {
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAssignments();
  }, []);

  const fetchAssignments = async () => {
    try {
      const data = await parkingService.getAssignments();
      setAssignments(data.results || data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching assignments:', error);
      setLoading(false);
    }
  };

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'active':
        return 'badge-success';
      case 'completed':
        return 'badge-info';
      case 'cancelled':
        return 'badge-danger';
      default:
        return 'badge-warning';
    }
  };

  if (loading) {
    return <main className="container"><p>Loading assignments...</p></main>;
  }

  return (
    <main className="container">
      <h1>🚗 Your Parking Assignments</h1>

      {assignments.length === 0 ? (
        <div className="card">
          <p>No assignments yet. Create a schedule to get assigned a parking slot!</p>
        </div>
      ) : (
        <div className="assignments-list">
          {assignments.map(assignment => (
            <div key={assignment.id} className="card">
              <div className="assignment-header">
                <div>
                  <h3>Slot {assignment.parking_slot_info.slot_number}</h3>
                  <p className="assignment-lot">{assignment.parking_slot_info.lot_name}</p>
                </div>
                <span className={`badge ${getStatusBadgeClass(assignment.status)}`}>
                  {assignment.status}
                </span>
              </div>

              <div className="assignment-details">
                <div className="detail-row">
                  <strong>Type:</strong>
                  <span>{assignment.parking_slot_info.slot_type}</span>
                </div>
                <div className="detail-row">
                  <strong>Duration:</strong>
                  <span>
                    {new Date(assignment.start_datetime).toLocaleDateString()} {' '}
                    {new Date(assignment.start_datetime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} to{' '}
                    {new Date(assignment.end_datetime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
                <div className="detail-row">
                  <strong>Distance:</strong>
                  <span>{Math.round(assignment.distance_to_building)}m away</span>
                </div>
                <div className="detail-row">
                  <strong>AI Score:</strong>
                  <span>
                    <div className="confidence-bar">
                      <div
                        className="confidence-fill"
                        style={{ width: `${assignment.ai_confidence_score * 100}%` }}
                      />
                    </div>
                    {Math.round(assignment.ai_confidence_score * 100)}%
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}

export default AssignmentsPage;
