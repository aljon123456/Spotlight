"""Admin configuration for parking app."""
from django.contrib import admin
from .models import (
    Campus, Building, ParkingLot, ParkingSlot, Schedule,
    Assignment, Notification, AssignmentHistory, NoShowTracking
)


@admin.register(Campus)
class CampusAdmin(admin.ModelAdmin):
    """Admin interface for Campus model."""
    list_display = ('name', 'city', 'state', 'total_parking_slots', 'created_at')
    list_filter = ('city', 'state', 'created_at')
    search_fields = ('name', 'location', 'city')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    """Admin interface for Building model."""
    list_display = ('name', 'code', 'campus', 'created_at')
    list_filter = ('campus', 'created_at')
    search_fields = ('name', 'code')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ParkingLot)
class ParkingLotAdmin(admin.ModelAdmin):
    """Admin interface for ParkingLot model."""
    list_display = ('name', 'campus', 'surface_type', 'available_slots', 'total_slots', 'created_at')
    list_filter = ('campus', 'surface_type', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ParkingSlot)
class ParkingSlotAdmin(admin.ModelAdmin):
    """Admin interface for ParkingSlot model."""
    list_display = ('slot_number', 'parking_lot', 'slot_type', 'status', 'created_at')
    list_filter = ('status', 'slot_type', 'parking_lot', 'created_at')
    search_fields = ('slot_number',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    """Admin interface for Schedule model."""
    list_display = ('title', 'user', 'schedule_type', 'building', 'start_date', 'end_date')
    list_filter = ('schedule_type', 'building', 'start_date', 'created_at')
    search_fields = ('title', 'user__username')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    """Admin interface for Assignment model."""
    list_display = ('user', 'parking_slot', 'status', 'start_datetime', 'end_datetime', 'ai_confidence_score')
    list_filter = ('status', 'start_datetime', 'created_at')
    search_fields = ('user__username', 'parking_slot__slot_number')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for Notification model."""
    list_display = ('user', 'title', 'notification_type', 'priority', 'is_read', 'created_at')
    list_filter = ('notification_type', 'priority', 'is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')
    readonly_fields = ('created_at',)


@admin.register(AssignmentHistory)
class AssignmentHistoryAdmin(admin.ModelAdmin):
    """Admin interface for AssignmentHistory model."""
    list_display = ('assignment', 'previous_slot', 'new_slot', 'change_reason', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('assignment__user__username', 'change_reason')
    readonly_fields = ('created_at',)


@admin.register(NoShowTracking)
class NoShowTrackingAdmin(admin.ModelAdmin):
    """Admin interface for NoShowTracking model."""
    list_display = ('user', 'assignment', 'was_notified', 'created_at')
    list_filter = ('was_notified', 'created_at')
    search_fields = ('user__username', 'assignment__parking_slot__slot_number')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_readonly_fields(self, request, obj=None):
        """Make reason editable for admins to note causes."""
        if obj:
            return self.readonly_fields + ('user', 'assignment')
        return self.readonly_fields

