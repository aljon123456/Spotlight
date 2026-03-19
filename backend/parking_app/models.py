"""
Parking app models.
Includes Campus, Building, ParkingLot, ParkingSlot, Schedule, Assignment, and Notification models.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()


class Campus(models.Model):
    """
    Campus model representing the university/campus.
    Contains multiple buildings and parking lots.
    """
    name = models.CharField(max_length=200, unique=True)
    location = models.CharField(max_length=300)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=10)
    total_parking_slots = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Campus'
        verbose_name_plural = 'Campuses'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Building(models.Model):
    """
    Building model representing campus buildings.
    Students attend classes and employees work in buildings.
    """
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name='buildings')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50)  # e.g., "ENGR", "SCI"
    description = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Building'
        verbose_name_plural = 'Buildings'
        unique_together = ('campus', 'code')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class ParkingLot(models.Model):
    """
    Parking Lot model representing specific parking areas.
    Multiple slots belong to one lot.
    """
    SURFACE_TYPE_CHOICES = (
        ('outdoor', 'Outdoor'),
        ('covered', 'Covered Parking'),
        ('garage', 'Parking Garage'),
        ('underground', 'Underground'),
    )
    
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name='parking_lots')
    name = models.CharField(max_length=200)
    surface_type = models.CharField(max_length=50, choices=SURFACE_TYPE_CHOICES)
    total_slots = models.IntegerField(validators=[MinValueValidator(1)])
    available_slots = models.IntegerField(validators=[MinValueValidator(0)])
    nearest_building = models.ForeignKey(Building, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Parking Lot'
        verbose_name_plural = 'Parking Lots'
        unique_together = ('campus', 'name')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.available_slots}/{self.total_slots})"


class ParkingSlot(models.Model):
    """
    Individual parking slot model.
    Represents single parking spaces that can be assigned to users.
    """
    SLOT_TYPE_CHOICES = (
        ('regular', 'Regular'),
        ('reserved', 'Reserved'),
        ('handicap', 'Handicap Accessible'),
        ('premium', 'Premium (Priority)'),
    )
    
    SLOT_STATUS_CHOICES = (
        ('available', 'Available'),
        ('assigned', 'Assigned'),
        ('maintenance', 'Maintenance'),
        ('blocked', 'Blocked'),
    )
    
    parking_lot = models.ForeignKey(ParkingLot, on_delete=models.CASCADE, related_name='slots')
    slot_number = models.CharField(max_length=50)
    slot_type = models.CharField(max_length=50, choices=SLOT_TYPE_CHOICES, default='regular')
    status = models.CharField(max_length=50, choices=SLOT_STATUS_CHOICES, default='available')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Parking Slot'
        verbose_name_plural = 'Parking Slots'
        unique_together = ('parking_lot', 'slot_number')
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['slot_type']),
        ]
        ordering = ['parking_lot', 'slot_number']
    
    def __str__(self):
        return f"{self.parking_lot.name} - {self.slot_number} ({self.status})"


class Schedule(models.Model):
    """
    Schedule model for students and employees.
    Contains class/work schedule information for parking assignment logic.
    """
    SCHEDULE_TYPE_CHOICES = (
        ('class', 'Class Schedule'),
        ('work', 'Work Schedule'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='schedules')
    schedule_type = models.CharField(max_length=20, choices=SCHEDULE_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    building = models.ForeignKey(Building, on_delete=models.SET_NULL, null=True)
    
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    days_of_week = models.CharField(
        max_length=100,
        help_text="Comma-separated days: Monday,Tuesday,Wednesday,Thursday,Friday"
    )
    
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Document upload for schedule verification
    schedule_document = models.FileField(
        upload_to='documents/',
        blank=True,
        null=True,
        help_text="Upload syllabus, schedule, or verification document (PDF, max 5MB)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Schedule'
        verbose_name_plural = 'Schedules'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def is_active(self):
        """Check if schedule is still active (within date range)."""
        from django.utils import timezone
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date


class Assignment(models.Model):
    """
    Parking assignment model.
    Links users to assigned parking slots with temporal information.
    Includes user confirmation mechanism with 30-minute grace period.
    """
    ASSIGNMENT_STATUS_CHOICES = (
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No-Show - Slot Released'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='parking_assignments')
    parking_slot = models.ForeignKey(ParkingSlot, on_delete=models.SET_NULL, null=True, blank=True)
    schedule = models.ForeignKey(Schedule, on_delete=models.SET_NULL, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=ASSIGNMENT_STATUS_CHOICES, default='active')
    
    # Confirmation tracking (30-minute grace period)
    is_confirmed = models.BooleanField(default=False, help_text="User confirmed arrival at parking lot")
    confirmed_at = models.DateTimeField(null=True, blank=True, help_text="When user confirmed arrival")
    confirmation_deadline = models.DateTimeField(null=True, blank=True, help_text="Deadline for user to confirm (30 mins after assignment)")
    
    assignment_date = models.DateField(auto_now_add=True)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    
    distance_to_building = models.FloatField(null=True, blank=True, help_text="Distance in meters")
    ai_confidence_score = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0.0)])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Assignment'
        verbose_name_plural = 'Assignments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['parking_slot', 'status']),
            models.Index(fields=['is_confirmed', 'status']),
        ]
    
    def __str__(self):
        return f"{self.user.username} -> {self.parking_slot} ({self.status})"


class Notification(models.Model):
    """
    Notification model for user alerts.
    Notifies users about assignments, changes, and system events.
    """
    NOTIFICATION_TYPE_CHOICES = (
        ('assignment', 'Parking Assignment'),
        ('change', 'Assignment Changed'),
        ('reminder', 'Parking Reminder'),
        ('alert', 'System Alert'),
        ('offer', 'Slot Offer'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPE_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    related_assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


class AssignmentHistory(models.Model):
    """
    History model for tracking assignment changes and audit trail.
    Records all modifications to parking assignments.
    """
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='history')
    previous_slot = models.ForeignKey(
        ParkingSlot, on_delete=models.SET_NULL, null=True, blank=True, related_name='+'
    )
    new_slot = models.ForeignKey(
        ParkingSlot, on_delete=models.SET_NULL, null=True, blank=True, related_name='+'
    )
    
    change_reason = models.CharField(max_length=200)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Assignment History'
        verbose_name_plural = 'Assignment History'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"History: {self.assignment}"


class NoShowTracking(models.Model):
    """
    Tracks user no-show incidents for parking assignments.
    Used to monitor and penalize repeat offenders.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='no_shows')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='no_show_record')
    
    was_notified = models.BooleanField(default=False, help_text="Whether user was notified about no-show")
    reason = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Reason provided by user (optional)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'No-Show Tracking'
        verbose_name_plural = 'No-Show Tracking'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - No-show on {self.assignment.schedule.title}"

