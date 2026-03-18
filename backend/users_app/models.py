"""
User models for SpotLight
Includes User, Student, Employee, and Subscription models
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator

class User(AbstractUser):
    """
    Extended user model with parking system specific fields.
    Can be Student or Employee based on user_type.
    """
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('employee', 'Employee'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    vehicle_plate = models.CharField(max_length=20, blank=True, null=True)
    vehicle_type = models.CharField(max_length=50, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.user_type})"


class Student(models.Model):
    """
    Student-specific model with academic information.
    Linked to User model via one-to-one relationship.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True)
    major = models.CharField(max_length=100, blank=True, null=True)
    year = models.IntegerField(choices=[(1, 'Freshman'), (2, 'Sophomore'), (3, 'Junior'), (4, 'Senior')], null=True)
    gpa = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0.0)])
    campus_building = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
        ordering = ['student_id']
    
    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name()}"


class Employee(models.Model):
    """
    Employee-specific model with department information.
    Linked to User model via one-to-one relationship.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    office_building = models.CharField(max_length=100)
    office_number = models.CharField(max_length=20)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
        ordering = ['employee_id']
    
    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name()}"


class Subscription(models.Model):
    """
    Subscription model for priority parking.
    Users can have active subscriptions for enhanced parking privileges.
    """
    SUBSCRIPTION_TYPE_CHOICES = (
        ('basic', 'Basic - Standard Parking'),
        ('premium', 'Premium - Priority Parking'),
        ('vip', 'VIP - Reserved Premium Spots'),
    )
    
    SUBSCRIPTION_STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    subscription_type = models.CharField(max_length=20, choices=SUBSCRIPTION_TYPE_CHOICES, default='basic')
    status = models.CharField(max_length=20, choices=SUBSCRIPTION_STATUS_CHOICES, default='active')
    
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_auto_renew = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.subscription_type} ({self.status})"
    
    def is_active(self):
        """Check if subscription is currently active."""
        from django.utils import timezone
        return self.status == 'active' and self.end_date > timezone.now()
