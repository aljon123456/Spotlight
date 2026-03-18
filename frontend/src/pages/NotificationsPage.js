// Notifications Page component
import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import { parkingService } from '../services/parkingService';
import './Pages.css';

function NotificationsPage() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch notifications immediately
    fetchNotifications();
    
    // Auto-refresh notifications every 5 seconds
    const interval = setInterval(() => {
      fetchNotifications();
    }, 5000);
    
    // Cleanup interval on unmount
    return () => clearInterval(interval);
  }, []);

  const fetchNotifications = async () => {
    try {
      const data = await parkingService.getNotifications();
      setNotifications(data.results || data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching notifications:', error);
      setLoading(false);
    }
  };

  const handleMarkAsRead = async (notificationId) => {
    try {
      await parkingService.markNotificationAsRead(notificationId);
      fetchNotifications();
      toast.success('Notification marked as read');
    } catch (error) {
      toast.error('Failed to mark notification');
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await parkingService.markAllNotificationsAsRead();
      fetchNotifications();
      toast.success('All notifications marked as read');
    } catch (error) {
      toast.error('Failed to mark all notifications');
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'urgent':
        return '#dc3545';
      case 'high':
        return '#fd7e14';
      case 'medium':
        return '#ffc107';
      case 'low':
        return '#17a2b8';
      default:
        return '#6c757d';
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'assignment':
        return '✓';
      case 'change':
        return '↻';
      case 'reminder':
        return '⏰';
      case 'alert':
        return '⚠';
      case 'offer':
        return '🎁';
      default:
        return '📬';
    }
  };

  if (loading) {
    return <main className="container"><p>Loading notifications...</p></main>;
  }

  const unreadCount = notifications.filter(n => !n.is_read).length;

  return (
    <main className="container">
      <div className="page-header">
        <h1>🔔 Notifications</h1>
        {unreadCount > 0 && (
          <button onClick={handleMarkAllAsRead} className="btn-secondary">
            Mark All as Read ({unreadCount})
          </button>
        )}
      </div>

      {notifications.length === 0 ? (
        <div className="card">
          <p>No notifications yet!</p>
        </div>
      ) : (
        <div className="notifications-list">
          {notifications.map(notification => (
            <div key={notification.id} className={`card notification ${!notification.is_read ? 'unread' : ''}`}>
              <div className="notification-header">
                <div className="notification-icon" style={{ color: getPriorityColor(notification.priority) }}>
                  {getTypeIcon(notification.notification_type)}
                </div>
                <div className="notification-content">
                  <h3>{notification.title}</h3>
                  <p>{notification.message}</p>
                  <small className="notification-time">
                    {new Date(notification.created_at).toLocaleString()}
                  </small>
                </div>
                {!notification.is_read && (
                  <button
                    onClick={() => handleMarkAsRead(notification.id)}
                    className="btn-small btn-primary"
                  >
                    Mark as read
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}

export default NotificationsPage;
