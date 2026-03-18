// Parking service for parking-related API calls
import apiClient from './api';

export const parkingService = {
  // Campus endpoints
  getCampuses: async () => {
    const response = await apiClient.get('/campus/');
    return response.data;
  },

  getCampusById: async (id) => {
    const response = await apiClient.get(`/campus/${id}/`);
    return response.data;
  },

  // Building endpoints
  getBuildings: async (campusId) => {
    const response = await apiClient.get('/buildings/', {
      params: { campus: campusId },
    });
    return response.data;
  },

  // Parking Lot endpoints
  getParkingLots: async (campusId) => {
    const response = await apiClient.get('/parking-lots/', {
      params: { campus: campusId },
    });
    return response.data;
  },

  getAvailableLots: async () => {
    const response = await apiClient.get('/parking-lots/available_lots/');
    return response.data;
  },

  // Parking Slot endpoints
  getParkingSlots: async (lotId) => {
    const response = await apiClient.get('/parking-slots/', {
      params: { parking_lot: lotId },
    });
    return response.data;
  },

  getAvailableSlots: async (slotType) => {
    const response = await apiClient.get('/parking-slots/available_slots/', {
      params: slotType ? { type: slotType } : {},
    });
    return response.data;
  },

  // Schedule endpoints
  getSchedules: async () => {
    const response = await apiClient.get('/schedules/');
    return response.data;
  },

  createSchedule: async (scheduleData) => {
    const response = await apiClient.post('/schedules/', scheduleData);
    return response.data;
  },

  updateSchedule: async (id, scheduleData) => {
    const response = await apiClient.put(`/schedules/${id}/`, scheduleData);
    return response.data;
  },

  deleteSchedule: async (id) => {
    await apiClient.delete(`/schedules/${id}/`);
  },

  assignParkingForSchedule: async (scheduleId) => {
    const response = await apiClient.post(`/schedules/${scheduleId}/assign_parking/`);
    return response.data;
  },

  // Assignment endpoints
  getAssignments: async () => {
    const response = await apiClient.get('/assignments/');
    return response.data;
  },

  getCurrentAssignment: async () => {
    const response = await apiClient.get('/assignments/current_assignment/');
    return response.data;
  },

  getAssignmentExplanation: async (assignmentId) => {
    const response = await apiClient.post(`/assignments/${assignmentId}/explain/`);
    return response.data;
  },

  // Notification endpoints
  getNotifications: async () => {
    const response = await apiClient.get('/notifications/');
    return response.data;
  },

  getUnreadNotifications: async () => {
    const response = await apiClient.get('/notifications/unread/');
    return response.data;
  },

  markNotificationAsRead: async (notificationId) => {
    const response = await apiClient.post(`/notifications/${notificationId}/mark_as_read/`);
    return response.data;
  },

  markAllNotificationsAsRead: async () => {
    const response = await apiClient.post('/notifications/mark_all_as_read/');
    return response.data;
  },
};
