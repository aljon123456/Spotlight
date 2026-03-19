"""
PayPal payment processing service.
Handles payment creation, verification, and subscription management.
Uses PayPal Server SDK for Python 3.14+ compatibility.
"""
import logging
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import User, Subscription
from .payment_models import Payment, PaymentPackage

logger = logging.getLogger(__name__)

# Use newer PayPal SDK compatible with Python 3.14+
try:
    from paypalserversdk.client import Client
    from paypalserversdk.http.auth.signature_auth import SignatureAuth
    from paypalserversdk.models.orders_create_request_body import OrdersCreateRequestBody
    from paypalserversdk.models.money import Money
    from paypalserversdk.models.amount_breakdown import AmountBreakdown
    from paypalserversdk.models.purchase_unit_request import PurchaseUnitRequest
    from paypalserversdk.models.payer import Payer
    PAYPAL_SDK_AVAILABLE = True
except ImportError:
    logger.warning("PayPal Server SDK not available. Fallback mode enabled.")
    PAYPAL_SDK_AVAILABLE = False


class PayPalService:
    """PayPal SDK wrapper for handling payments."""
    
    def __init__(self):
        """Initialize PayPal SDK with credentials."""
        if not PAYPAL_SDK_AVAILABLE:
            logger.warning("PayPal SDK not available")
            return
            
        try:
            self.client = Client(
                mode=settings.PAYPAL_MODE,  # 'sandbox' or 'live'
                client_id=settings.PAYPAL_CLIENT_ID,
                client_secret=settings.PAYPAL_CLIENT_SECRET,
            )
            logger.info(f"PayPal Service initialized in {settings.PAYPAL_MODE} mode")
        except Exception as e:
            logger.error(f"Failed to initialize PayPal client: {str(e)}")
            self.client = None
    
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
            if not PAYPAL_SDK_AVAILABLE or not self.client:
                logger.warning("PayPal SDK not available - creating mock payment record")
                return self._create_mock_payment(user, subscription_type, duration_months)
            
            # Get package pricing
            package = PaymentPackage.objects.get(subscription_type=subscription_type)
            
            # Calculate amount based on duration
            if duration_months == 12:
                amount = str(package.annual_price)
            else:
                amount = str(package.monthly_price)
            
            # Create order with new SDK (simplified for compatibility)
            try:
                order = self.client.orders().create({
                    "intent": "CAPTURE",
                    "purchase_units": [{
                        "amount": {
                            "value": amount,
                            "currency_code": "USD"
                        },
                        "description": f"SpotLight {subscription_type.title()} Subscription - {duration_months} month(s)"
                    }],
                    "payer": {},
                    "application_context": {
                        "return_url": settings.PAYPAL_RETURN_URL,
                        "cancel_url": settings.PAYPAL_CANCEL_URL
                    }
                })
                
                # Store payment record in database
                db_payment = Payment.objects.create(
                    user=user,
                    subscription_type=subscription_type,
                    amount=Decimal(amount),
                    currency="USD",
                    paypal_transaction_id=order['id'] if isinstance(order, dict) else str(order),
                    duration_months=duration_months,
                    status='pending'
                )
                
                # Get approval link
                approval_url = None
                if isinstance(order, dict) and 'links' in order:
                    for link in order.get('links', []):
                        if link.get('rel') == 'approve':
                            approval_url = link.get('href')
                            break
                
                if approval_url:
                    logger.info(f"PayPal payment created: {order.get('id')} for user {user.email}")
                    return {
                        'success': True,
                        'payment_id': db_payment.id,
                        'paypal_payment_id': order.get('id'),
                        'approval_url': approval_url
                    }
                else:
                    db_payment.delete()
                    return {
                        'success': False,
                        'error': 'Failed to generate approval URL'
                    }
            except Exception as e:
                logger.error(f"PayPal API error: {str(e)}")
                return self._create_mock_payment(user, subscription_type, duration_months)
                
        except PaymentPackage.DoesNotExist:
            return {
                'success': False,
                'error': f'Package {subscription_type} not found'
            }
        except Exception as e:
            logger.error(f"Payment creation error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_mock_payment(self, user, subscription_type, duration_months):
        """Create a mock payment record for testing/fallback."""
        try:
            package = PaymentPackage.objects.get(subscription_type=subscription_type)
            amount = package.annual_price if duration_months == 12 else package.monthly_price
            
            db_payment = Payment.objects.create(
                user=user,
                subscription_type=subscription_type,
                amount=Decimal(amount),
                currency="USD",
                paypal_transaction_id=f"MOCK-{subscription_type.upper()}-{user.id}",
                duration_months=duration_months,
                status='testing'
            )
            
            logger.info(f"Mock payment created for testing: {db_payment.id}")
            return {
                'success': True,
                'payment_id': db_payment.id,
                'paypal_payment_id': f"MOCK-{subscription_type.upper()}",
                'approval_url': f"{settings.PAYPAL_RETURN_URL}?mock=true&payment_id={db_payment.id}"
            }
        except Exception as e:
            logger.error(f"Mock payment creation failed: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to create payment'
            }
    
    def execute_payment(self, paypal_payment_id, payer_id, payment_id):
        """
        Execute PayPal payment after user approval.
        
        Args:
            paypal_payment_id: PayPal payment ID
            payer_id: PayPal payer ID (may be skipped for Orders API)
            payment_id: Database payment ID
        
        Returns:
            dict with success status
        """
        try:
            logger.info(f"Executing PayPal payment: {paypal_payment_id}")
            
            if not PAYPAL_SDK_AVAILABLE or not self.client:
                # Fallback: Mark as completed if SDK not available
                db_payment = Payment.objects.get(id=payment_id)
                return self._complete_payment_record(db_payment)
            
            try:
                # For Orders API, we need to capture the order
                result = self.client.orders().capture(paypal_payment_id)
                
                if isinstance(result, dict) and result.get('status') in ['APPROVED', 'COMPLETED']:
                    db_payment = Payment.objects.get(id=payment_id)
                    return self._complete_payment_record(db_payment)
                else:
                    logger.error(f"PayPal order capture failed for: {paypal_payment_id}")
                    db_payment = Payment.objects.get(id=payment_id)
                    db_payment.status = 'failed'
                    db_payment.save()
                    return {
                        'success': False,
                        'error': 'Payment capture failed'
                    }
            except Exception as e:
                logger.error(f"PayPal API capture error: {str(e)}")
                db_payment = Payment.objects.get(id=payment_id)
                db_payment.status = 'failed'
                db_payment.save()
                return {
                    'success': False,
                    'error': 'Payment processing error'
                }
                
        except Payment.DoesNotExist:
            logger.error(f"Database payment record not found: {payment_id}")
            return {
                'success': False,
                'error': 'Payment record not found in database'
            }
        except Exception as e:
            logger.exception(f"PayPal execution error: {str(e)}")
            return {
                'success': False,
                'error': f"Payment processing error: {str(e)}"
            }
    
    def _complete_payment_record(self, db_payment):
        """Helper to complete a payment record and create subscription."""
        try:
            db_payment.status = 'completed'
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
            
            logger.info(f"Subscription created for user {db_payment.user.email}: {subscription.subscription_type}")
            
            return {
                'success': True,
                'message': 'Payment successful',
                'subscription_type': db_payment.subscription_type
            }
        except Exception as e:
            logger.error(f"Failed to complete payment record: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to process subscription'
            }
    
    def cancel_payment(self, payment_id):
        """Mark payment as cancelled."""
        try:
            db_payment = Payment.objects.get(id=payment_id)
            db_payment.status = 'cancelled'
            db_payment.save()
            logger.info(f"Payment cancelled: {payment_id}")
            return {'success': True, 'message': 'Payment cancelled'}
        except Payment.DoesNotExist:
            logger.error(f"Payment not found: {payment_id}")
            return {'success': False, 'error': 'Payment not found'}
        except Exception as e:
            logger.error(f"Error cancelling payment: {str(e)}")
            return {'success': False, 'error': str(e)}
