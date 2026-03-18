"""
Payment models for handling PayPal transactions and subscription purchases.
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Payment(models.Model):
    """
    Payment model to track PayPal transactions.
    Records every payment attempt and subscription purchase.
    """
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    )
    
    SUBSCRIPTION_TYPE_CHOICES = (
        ('basic', 'Basic - Standard Parking'),
        ('premium', 'Premium - Priority Parking'),
        ('vip', 'VIP - Reserved Premium Spots'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    subscription_type = models.CharField(max_length=20, choices=SUBSCRIPTION_TYPE_CHOICES)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    # PayPal transaction details
    paypal_transaction_id = models.CharField(max_length=100, unique=True, db_index=True)
    paypal_subscription_id = models.CharField(max_length=100, blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Subscription duration
    duration_months = models.IntegerField(default=1)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['paypal_transaction_id']),
            models.Index(fields=['user', 'status']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.subscription_type} - ${self.amount}"


class PaymentPackage(models.Model):
    """
    Pre-defined payment packages for subscriptions.
    Allows admin to manage pricing and features.
    """
    SUBSCRIPTION_TYPE_CHOICES = (
        ('basic', 'Basic - Standard Parking'),
        ('premium', 'Premium - Priority Parking'),
        ('vip', 'VIP - Reserved Premium Spots'),
    )
    
    subscription_type = models.CharField(
        max_length=20, 
        choices=SUBSCRIPTION_TYPE_CHOICES, 
        unique=True,
        primary_key=True
    )
    
    monthly_price = models.DecimalField(max_digits=10, decimal_places=2)
    annual_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    features = models.TextField(
        help_text="Comma-separated list of features for this package"
    )
    
    max_active_reservations = models.IntegerField(default=1)
    priority_slot_access = models.BooleanField(default=False)
    reserved_spots = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Payment Package'
        verbose_name_plural = 'Payment Packages'
    
    def __str__(self):
        return f"{self.subscription_type.title()} - ${self.monthly_price}/month"
