"""
Payment views for handling PayPal transactions and subscriptions.
"""
from rest_framework import status, generics, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .payment_models import Payment, PaymentPackage
from .payment_serializers import (
    PaymentSerializer, PaymentPackageSerializer, 
    PaymentInitSerializer, PaymentExecuteSerializer
)
from .paypal_service import PayPalService


class PaymentPackageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset for payment packages.
    Shows available subscription plans.
    """
    queryset = PaymentPackage.objects.filter(is_active=True)
    serializer_class = PaymentPackageSerializer
    permission_classes = (IsAuthenticated,)


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset for viewing payment history."""
    serializer_class = PaymentSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        """Get payments for current user."""
        return Payment.objects.filter(user=self.request.user)


class PaymentInitiateView(generics.CreateAPIView):
    """
    Initiate a PayPal payment.
    Returns approval URL for user to redirect to PayPal.
    """
    serializer_class = PaymentInitSerializer
    permission_classes = (IsAuthenticated,)
    
    def create(self, request, *args, **kwargs):
        """Create payment and return PayPal approval URL."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        paypal_service = PayPalService()
        result = paypal_service.create_payment(
            user=request.user,
            subscription_type=serializer.validated_data['subscription_type'],
            duration_months=serializer.validated_data.get('duration_months', 1)
        )
        
        if result['success']:
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': result['error']},
                status=status.HTTP_400_BAD_REQUEST
            )


class PaymentExecuteView(generics.CreateAPIView):
    """
    Execute PayPal payment after user approval.
    Called after user approves payment on PayPal.
    """
    serializer_class = PaymentExecuteSerializer
    permission_classes = (IsAuthenticated,)
    
    def create(self, request, *args, **kwargs):
        """Execute payment and create subscription."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        paypal_service = PayPalService()
        result = paypal_service.execute_payment(
            paypal_payment_id=serializer.validated_data['paypal_payment_id'],
            payer_id=serializer.validated_data['payer_id'],
            payment_id=serializer.validated_data['payment_id']
        )
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': result['error']},
                status=status.HTTP_400_BAD_REQUEST
            )


class PaymentCancelView(generics.CreateAPIView):
    """Cancel a pending payment."""
    permission_classes = (IsAuthenticated,)
    
    def create(self, request, *args, **kwargs):
        """Cancel payment."""
        payment_id = request.data.get('payment_id')
        
        if not payment_id:
            return Response(
                {'error': 'payment_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        paypal_service = PayPalService()
        result = paypal_service.cancel_payment(payment_id)
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': result.get('error', 'Failed to cancel payment')},
                status=status.HTTP_400_BAD_REQUEST
            )


class SubscriptionInfoView(generics.RetrieveAPIView):
    """Get current user's subscription info."""
    permission_classes = (IsAuthenticated,)
    
    def retrieve(self, request, *args, **kwargs):
        """Return user's current subscription."""
        from .models import Subscription
        
        try:
            subscription = Subscription.objects.get(user=request.user)
            from .serializers import SubscriptionSerializer
            serializer = SubscriptionSerializer(subscription)
            return Response(serializer.data)
        except Subscription.DoesNotExist:
            return Response(
                {'subscription_type': 'basic', 'status': 'inactive'},
                status=status.HTTP_200_OK
            )
