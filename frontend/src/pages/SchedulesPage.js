// Schedules Page component
import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import { parkingService } from '../services/parkingService';
import './Pages.css';

function SchedulesPage() {
  const [schedules, setSchedules] = useState([]);
  const [buildings, setBuildings] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    schedule_type: 'class',
    title: '',
    building: '',
    start_time: '09:00',
    end_time: '10:00',
    days_of_week: 'Monday,Tuesday,Wednesday,Thursday,Friday',
    start_date: new Date().toISOString().split('T')[0],
    end_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
  });

  useEffect(() => {
    fetchSchedules();
    fetchCampusAndBuildings();
  }, []);

  const fetchSchedules = async () => {
    try {
      const data = await parkingService.getSchedules();
      setSchedules(data.results || data);
      setLoading(false);
    } catch (error) {
      toast.error('Failed to load schedules');
      setLoading(false);
    }
  };

  const fetchCampusAndBuildings = async () => {
    try {
      // First fetch campuses to get the correct ID
      const campusData = await parkingService.getCampuses();
      const campuses = campusData.results || campusData;
      
      if (campuses.length > 0) {
        const campus = campuses[0];
        
        // Then fetch buildings for that campus
        const buildingsData = await parkingService.getBuildings(campus.id);
        setBuildings(buildingsData.results || buildingsData);
      } else {
        console.warn('No campuses found');
        setBuildings([]);
      }
    } catch (error) {
      console.error('Error fetching campus or buildings:', error);
      setBuildings([]);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await parkingService.createSchedule(formData);
      toast.success('Schedule created successfully!');
      setShowForm(false);
      setFormData({
        schedule_type: 'class',
        title: '',
        building: '',
        start_time: '09:00',
        end_time: '10:00',
        days_of_week: 'Monday,Tuesday,Wednesday,Thursday,Friday',
        start_date: new Date().toISOString().split('T')[0],
        end_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      });
      fetchSchedules();
    } catch (error) {
      toast.error('Failed to create schedule');
    }
  };

  const handleAssignParking = async (scheduleId) => {
    try {
      await parkingService.assignParkingForSchedule(scheduleId);
      toast.success('Parking assigned successfully!');
      fetchSchedules();
    } catch (error) {
      toast.error('Failed to assign parking');
    }
  };

  if (loading) {
    return <main className="container"><p>Loading schedules...</p></main>;
  }

  return (
    <main className="container">
      <div className="page-header">
        <h1>📚 Your Schedules</h1>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary">
          {showForm ? 'Cancel' : 'Add New Schedule'}
        </button>
      </div>

      {showForm && (
        <div className="card">
          <h2>Create New Schedule</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-row">
              <div className="form-group half">
                <label htmlFor="schedule_type">Type</label>
                <select
                  id="schedule_type"
                  name="schedule_type"
                  value={formData.schedule_type}
                  onChange={handleChange}
                >
                  <option value="class">Class</option>
                  <option value="work">Work</option>
                </select>
              </div>
              <div className="form-group half">
                <label htmlFor="title">Title</label>
                <input
                  type="text"
                  id="title"
                  name="title"
                  value={formData.title}
                  onChange={handleChange}
                  placeholder="e.g., CS 101 Lecture"
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="building">Building {buildings.length === 0 && '(No buildings available - field optional)'}</label>
              <select
                id="building"
                name="building"
                value={formData.building}
                onChange={handleChange}
                required={buildings.length > 0}
              >
                <option value="">Select a building...</option>
                {buildings.map(building => (
                  <option key={building.id} value={building.id}>
                    {building.name} ({building.code})
                  </option>
                ))}
              </select>
              {buildings.length === 0 && (
                <p style={{color: '#666', fontSize: '0.9em', marginTop: '5px'}}>
                  No buildings found for your campus. You can proceed without selecting a building.
                </p>
              )}
            </div>

            <div className="form-row">
              <div className="form-group half">
                <label htmlFor="start_time">Start Time</label>
                <input
                  type="time"
                  id="start_time"
                  name="start_time"
                  value={formData.start_time}
                  onChange={handleChange}
                  required
                />
              </div>
              <div className="form-group half">
                <label htmlFor="end_time">End Time</label>
                <input
                  type="time"
                  id="end_time"
                  name="end_time"
                  value={formData.end_time}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group half">
                <label htmlFor="start_date">Start Date</label>
                <input
                  type="date"
                  id="start_date"
                  name="start_date"
                  value={formData.start_date}
                  onChange={handleChange}
                  required
                />
              </div>
              <div className="form-group half">
                <label htmlFor="end_date">End Date</label>
                <input
                  type="date"
                  id="end_date"
                  name="end_date"
                  value={formData.end_date}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="days_of_week">Days of Week</label>
              <input
                type="text"
                id="days_of_week"
                name="days_of_week"
                value={formData.days_of_week}
                onChange={handleChange}
                placeholder="Monday,Tuesday,Wednesday,Thursday,Friday"
              />
            </div>

            <button type="submit" className="btn-primary">Create Schedule</button>
          </form>
        </div>
      )}

      <div className="schedules-list">
        {schedules.length === 0 ? (
          <p>No schedules yet. Create one to get started!</p>
        ) : (
          schedules.map(schedule => (
            <div key={schedule.id} className="card">
              <div className="schedule-header">
                <div>
                  <h3>{schedule.title}</h3>
                  <p className="schedule-meta">
                    {schedule.schedule_type === 'class' ? '📖' : '💼'} {schedule.building_name}
                  </p>
                </div>
                <span className="badge badge-info">
                  {schedule.start_time} - {schedule.end_time}
                </span>
              </div>
              <p className="schedule-date">
                {new Date(schedule.start_date).toLocaleDateString()} to{' '}
                {new Date(schedule.end_date).toLocaleDateString()}
              </p>
              <p className="schedule-days">{schedule.days_of_week}</p>
              <button
                onClick={() => handleAssignParking(schedule.id)}
                className="btn-success"
              >
                Assign Parking
              </button>
            </div>
          ))
        )}
      </div>
    </main>
  );
}

export default SchedulesPage;
