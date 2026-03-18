"""Admin configuration for users app."""
from django.contrib import admin
from .models import User, Student, Employee, Subscription
from .payment_models import Payment, PaymentPackage


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Admin interface for User model."""
    list_display = ('username', 'email', 'user_type', 'is_active', 'created_at')
    list_filter = ('user_type', 'is_active', 'created_at')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Admin interface for Student model."""
    list_display = ('student_id', 'user', 'major', 'year', 'campus_building')
    list_filter = ('year', 'created_at')
    search_fields = ('student_id', 'user__username', 'major')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Admin interface for Employee model."""
    list_display = ('employee_id', 'user', 'department', 'position', 'office_building')
    list_filter = ('department', 'created_at')
    search_fields = ('employee_id', 'user__username', 'department')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Admin interface for Subscription model."""
    list_display = ('user', 'subscription_type', 'status', 'start_date', 'end_date')
    list_filter = ('subscription_type', 'status', 'created_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'updated_at', 'start_date')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin interface for Payment model."""
    list_display = ('user', 'subscription_type', 'amount', 'status', 'created_at')
    list_filter = ('subscription_type', 'status', 'created_at')
    search_fields = ('user__username', 'paypal_transaction_id')
    readonly_fields = ('created_at', 'updated_at', 'paypal_transaction_id')


@admin.register(PaymentPackage)
class PaymentPackageAdmin(admin.ModelAdmin):
    """Admin interface for PaymentPackage model."""
    list_display = ('subscription_type', 'monthly_price', 'annual_price', 'is_active')
    list_filter = ('is_active', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
