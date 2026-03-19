"""
Serializers for parking app models.
Handles serialization for all parking-related entities.
"""
from rest_framework import serializers
from .models import (
    Campus, Building, ParkingLot, ParkingSlot, Schedule,
    Assignment, Notification, AssignmentHistory, NoShowTracking
)


class CampusSerializer(serializers.ModelSerializer):
    """Serializer for Campus model."""
    class Meta:
        model = Campus
        fields = ('id', 'name', 'location', 'city', 'state', 'zip_code', 'total_parking_slots', 'created_at')
        read_only_fields = ('id', 'created_at')


class BuildingSerializer(serializers.ModelSerializer):
    """Serializer for Building model."""
    campus_name = serializers.CharField(source='campus.name', read_only=True)
    
    class Meta:
        model = Building
        fields = ('id', 'campus', 'campus_name', 'name', 'code', 'description', 'created_at')
        read_only_fields = ('id', 'created_at', 'campus_name')


class ParkingLotSerializer(serializers.ModelSerializer):
    """Serializer for ParkingLot model."""
    campus_name = serializers.CharField(source='campus.name', read_only=True)
    nearest_building_name = serializers.CharField(source='nearest_building.name', read_only=True)
    
    class Meta:
        model = ParkingLot
        fields = (
            'id', 'campus', 'campus_name', 'name', 'surface_type',
            'total_slots', 'available_slots', 'nearest_building', 'nearest_building_name', 'created_at'
        )
        read_only_fields = ('id', 'created_at', 'campus_name', 'nearest_building_name')


class ParkingSlotSerializer(serializers.ModelSerializer):
    """Serializer for ParkingSlot model."""
    lot_name = serializers.CharField(source='parking_lot.name', read_only=True)
    
    class Meta:
        model = ParkingSlot
        fields = ('id', 'parking_lot', 'lot_name', 'slot_number', 'slot_type', 'status', 'created_at')
        read_only_fields = ('id', 'created_at', 'lot_name')


class ScheduleSerializer(serializers.ModelSerializer):
    """Serializer for Schedule model."""
    building_name = serializers.CharField(source='building.name', read_only=True, allow_null=True)
    is_active = serializers.SerializerMethodField()
    schedule_document_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Schedule
        fields = (
            'id', 'user', 'schedule_type', 'title', 'building', 'building_name',
            'start_time', 'end_time', 'days_of_week', 'start_date', 'end_date',
            'schedule_document', 'schedule_document_url', 'is_active', 'created_at'
        )
        read_only_fields = ('id', 'created_at', 'building_name', 'user', 'is_active', 'schedule_document_url')
    
    def get_is_active(self, obj):
        """Check if schedule is currently active."""
        return obj.is_active()
    
    def get_schedule_document_url(self, obj):
        """Get URL for schedule document."""
        if obj.schedule_document:
            return obj.schedule_document.url
        return None


class AssignmentSerializer(serializers.ModelSerializer):
    """Serializer for Assignment model."""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    parking_slot_info = ParkingSlotSerializer(source='parking_slot', read_only=True)
    
    class Meta:
        model = Assignment
        fields = (
            'id', 'user', 'user_name', 'parking_slot', 'parking_slot_info', 'schedule',
            'status', 'assignment_date', 'start_datetime', 'end_datetime',
            'distance_to_building', 'ai_confidence_score', 'created_at'
        )
        read_only_fields = ('id', 'created_at', 'user_name', 'parking_slot_info')


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model."""
    class Meta:
        model = Notification
        fields = (
            'id', 'user', 'title', 'message', 'notification_type', 'priority',
            'is_read', 'read_at', 'related_assignment', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class AssignmentHistorySerializer(serializers.ModelSerializer):
    """Serializer for AssignmentHistory model."""
    previous_slot_info = ParkingSlotSerializer(source='previous_slot', read_only=True)
    new_slot_info = ParkingSlotSerializer(source='new_slot', read_only=True)
    changed_by_name = serializers.CharField(source='changed_by.get_full_name', read_only=True)
    
    class Meta:
        model = AssignmentHistory
        fields = (
            'id', 'assignment', 'previous_slot', 'previous_slot_info',
            'new_slot', 'new_slot_info', 'change_reason', 'changed_by', 'changed_by_name', 'created_at'
        )
        read_only_fields = ('id', 'created_at', 'previous_slot_info', 'new_slot_info', 'changed_by_name')


class NoShowTrackingSerializer(serializers.ModelSerializer):
    """Serializer for NoShowTracking model."""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    assignment_info = AssignmentSerializer(source='assignment', read_only=True)
    
    class Meta:
        model = NoShowTracking
        fields = (
            'id', 'user', 'user_name', 'assignment', 'assignment_info',
            'was_notified', 'reason', 'created_at'
        )
        read_only_fields = ('id', 'created_at', 'user_name', 'assignment_info', 'was_notified')

