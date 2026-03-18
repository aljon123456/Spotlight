"""
PayPal payment processing service.
Handles payment creation, verification, and subscription management.
"""
import paypalrestsdk
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import User, Subscription
from .payment_models import Payment, PaymentPackage


class PayPalService:
    """PayPal SDK wrapper for handling payments."""
    
    def __init__(self):
        """Initialize PayPal SDK with credentials."""
        paypalrestsdk.configure({
            "mode": settings.PAYPAL_MODE,  # sandbox or live
            "client_id": settings.PAYPAL_CLIENT_ID,
            "client_secret": settings.PAYPAL_CLIENT_SECRET,
        })
    
    def create_payment(self, user, subscription_type, duration_months=1):
        """
        Create a PayPal payment.
        
        Args:
            user: User object
            subscription_type: 'basic', 'premium', or 'vip'
            duration_months: Number of months (1 or 12)
        
        Returns:
            dict with payment details and redirect URL
        """
        try:
            # Get package pricing
            package = PaymentPackage.objects.get(subscription_type=subscription_type)
            
            # Calculate amount based on duration
            if duration_months == 12:
                amount = str(package.annual_price)
            else:
                amount = str(package.monthly_price)
            
            # Create PayPal payment
            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "redirect_urls": {
                    "return_url": settings.PAYPAL_RETURN_URL,
                    "cancel_url": settings.PAYPAL_CANCEL_URL
                },
                "transactions": [{
                    "item_list": {
                        "items": [{
                            "name": f"{subscription_type.title()} Subscription - {duration_months} month(s)",
                            "sku": f"SUB-{subscription_type.upper()}",
                            "price": amount,
                            "currency": "USD",
                            "quantity": 1
                        }]
                    },
                    "amount": {
                        "total": amount,
                        "currency": "USD",
                        "details": {
                            "subtotal": amount
                        }
                    },
                    "description": f"SpotLight {subscription_type.title()} Subscription"
                }]
            })
            
            if payment.create():
                # Store payment record in database
                db_payment = Payment.objects.create(
                    user=user,
                    subscription_type=subscription_type,
                    amount=Decimal(amount),
                    currency="USD",
                    paypal_transaction_id=payment.id,
                    duration_months=duration_months,
                    status='pending'
                )
                
                # Get approval URL
                for link in payment.links:
                    if link.rel == "approval_url":
                        return {
                            'success': True,
                            'payment_id': db_payment.id,
                            'paypal_payment_id': payment.id,
                            'approval_url': link.href
                        }
            else:
                return {
                    'success': False,
                    'error': payment.error['message']
                }
        except PaymentPackage.DoesNotExist:
            return {
                'success': False,
                'error': f'Package {subscription_type} not found'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def execute_payment(self, paypal_payment_id, payer_id, payment_id):
        """
        Execute PayPal payment after user approval.
        
        Args:
            paypal_payment_id: PayPal payment ID
            payer_id: PayPal payer ID
            payment_id: Database payment ID
        
        Returns:
            dict with success status
        """
        try:
            payment = paypalrestsdk.Payment.find(paypal_payment_id)
            
            if payment.execute({"payer_id": payer_id}):
                # Payment successful - update database
                db_payment = Payment.objects.get(id=payment_id)
                db_payment.status = 'completed'
                db_payment.paypal_subscription_id = payment.id
                db_payment.completed_at = timezone.now()
                db_payment.save()
                
                # Create/Update subscription
                subscription, created = Subscription.objects.update_or_create(
                    user=db_payment.user,
                    defaults={
                        'subscription_type': db_payment.subscription_type,
                        'status': 'active',
                        'start_date': timezone.now(),
                        'end_date': timezone.now() + timedelta(days=30*db_payment.duration_months),
                        'price': db_payment.amount,
                        'is_auto_renew': False,
                    }
                )
                
                return {
                    'success': True,
                    'message': 'Payment successful',
                    'subscription_type': db_payment.subscription_type
                }
            else:
                db_payment = Payment.objects.get(id=payment_id)
                db_payment.status = 'failed'
                db_payment.save()
                
                return {
                    'success': False,
                    'error': payment.error['message']
                }
        except Payment.DoesNotExist:
            return {
                'success': False,
                'error': 'Payment record not found'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def cancel_payment(self, payment_id):
        """Mark payment as cancelled."""
        try:
            db_payment = Payment.objects.get(id=payment_id)
            db_payment.status = 'cancelled'
            db_payment.save()
            return {'success': True}
        except Payment.DoesNotExist:
            return {'success': False, 'error': 'Payment not found'}
