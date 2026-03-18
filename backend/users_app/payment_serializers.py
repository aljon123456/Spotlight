"""
Serializers for Payment and PaymentPackage models.
"""
from rest_framework import serializers
from .payment_models import Payment, PaymentPackage


class PaymentPackageSerializer(serializers.ModelSerializer):
    """Serializer for payment packages."""
    features_list = serializers.SerializerMethodField()
    
    class Meta:
        model = PaymentPackage
        fields = (
            'subscription_type', 'monthly_price', 'annual_price', 
            'features', 'features_list', 'max_active_reservations',
            'priority_slot_access', 'reserved_spots', 'is_active'
        )
        read_only_fields = ('subscription_type',)
    
    def get_features_list(self, obj):
        """Convert comma-separated features to list."""
        return [f.strip() for f in obj.features.split(',')]


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payment transactions."""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Payment
        fields = (
            'id', 'user', 'user_name', 'subscription_type', 'amount', 
            'currency', 'status', 'duration_months', 'created_at', 
            'completed_at', 'paypal_transaction_id'
        )
        read_only_fields = ('id', 'user', 'paypal_transaction_id', 'created_at', 'completed_at')


class PaymentInitSerializer(serializers.Serializer):
    """Serializer for initiating a payment."""
    subscription_type = serializers.ChoiceField(
        choices=['basic', 'premium', 'vip'],
        help_text="Type of subscription package"
    )
    duration_months = serializers.IntegerField(
        default=1,
        help_text="1 for monthly or 12 for annual"
    )


class PaymentExecuteSerializer(serializers.Serializer):
    """Serializer for executing a payment."""
    paypal_payment_id = serializers.CharField()
    payer_id = serializers.CharField()
    payment_id = serializers.IntegerField()
