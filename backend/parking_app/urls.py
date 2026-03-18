"""
URL configuration for parking app.
Routes for campus, buildings, lots, slots, schedules, assignments, and notifications.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CampusViewSet, BuildingViewSet, ParkingLotViewSet, ParkingSlotViewSet,
    ScheduleViewSet, AssignmentViewSet, NotificationViewSet, AssignmentHistoryViewSet
)

router = DefaultRouter()
router.register(r'campus', CampusViewSet, basename='campus')
router.register(r'buildings', BuildingViewSet, basename='building')
router.register(r'parking-lots', ParkingLotViewSet, basename='parking-lot')
router.register(r'parking-slots', ParkingSlotViewSet, basename='parking-slot')
router.register(r'schedules', ScheduleViewSet, basename='schedule')
router.register(r'assignments', AssignmentViewSet, basename='assignment')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'assignment-history', AssignmentHistoryViewSet, basename='assignment-history')

urlpatterns = [
    path('', include(router.urls)),
]
