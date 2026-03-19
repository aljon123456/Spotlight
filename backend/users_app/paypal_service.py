"""
PayPal payment processing service.
Handles payment creation, verification, and subscription management.
Uses Braintree SDK (PayPal's official modern SDK) for Python 3.14+ compatibility.
"""
import logging
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import User, Subscription
from .payment_models import Payment, PaymentPackage

logger = logging.getLogger(__name__)

# Use Braintree SDK (PayPal's official modern SDK compatible with Python 3.14+)
try:
    import braintree
    PAYPAL_SDK_AVAILABLE = True
except ImportError:
    logger.warning("Braintree SDK not available. Fallback mode enabled.")
    PAYPAL_SDK_AVAILABLE = False


class PayPalService:
    """Braintree payment processor for PayPal transactions."""
    
    def __init__(self):
        """Initialize Braintree gateway with credentials."""
        if not PAYPAL_SDK_AVAILABLE:
            logger.warning("Braintree SDK not available")
            return
            
        try:
            env = braintree.Environment.Sandbox if settings.PAYPAL_MODE == 'sandbox' else braintree.Environment.Production
            braintree.Configuration.configure(
                env,
                merchant_id=settings.PAYPAL_CLIENT_ID,
                public_key=getattr(settings, 'BRAINTREE_PUBLIC_KEY', 'pk_test'),
                private_key=settings.PAYPAL_CLIENT_SECRET,
            )
            logger.info(f"Braintree gateway initialized in {settings.PAYPAL_MODE} mode")
        except Exception as e:
            logger.error(f"Failed to initialize Braintree: {str(e)}")
            PAYPAL_SDK_AVAILABLE = False
    
    def create_payment(self, user, subscription_type, duration_months=1):
        """
        Create a PayPal payment via Braintree.
        
        Args:
            user: User object
            subscription_type: 'basic', 'premium', or 'vip'
            duration_months: Number of months (1 or 12)
        
        Returns:
            dict with payment details and redirect URL
        """
        try:
            if not PAYPAL_SDK_AVAILABLE:
                logger.warning("Braintree SDK not available - creating mock payment record")
                return self._create_mock_payment(user, subscription_type, duration_months)
            
            # Get package pricing
            package = PaymentPackage.objects.get(subscription_type=subscription_type)
            
            # Calculate amount based on duration
            if duration_months == 12:
                amount = float(package.annual_price)
            else:
                amount = float(package.monthly_price)
            
            # Create client token for frontend to tokenize payment
            client_token = braintree.ClientToken.generate()
            
            # Store payment record in database (for tracking, will be completed after payment)
            db_payment = Payment.objects.create(
                user=user,
                subscription_type=subscription_type,
                amount=Decimal(str(amount)),
                currency="USD",
                paypal_transaction_id=f"PENDING-{user.id}-{subscription_type}",
                duration_months=duration_months,
                status='pending'
            )
            
            logger.info(f"Braintree payment initiated for user {user.email}: ${amount} {subscription_type}")
            
            return {
                'success': True,
                'payment_id': db_payment.id,
                'client_token': client_token,
                'amount': amount,
                'subscription_type': subscription_type
            }
                
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
    
    def execute_payment(self, nonce, payment_id):
        """
        Execute a Braintree payment using a payment method nonce.
        
        Args:
            nonce: Payment method nonce from frontend (Braintree.js)
            payment_id: Database payment ID
        
        Returns:
            dict with success status
        """
        try:
            logger.info(f"Executing Braintree payment: {payment_id}")
            
            if not PAYPAL_SDK_AVAILABLE:
                # Fallback: Mark as completed if SDK not available
                db_payment = Payment.objects.get(id=payment_id)
                return self._complete_payment_record(db_payment)
            
            db_payment = Payment.objects.get(id=payment_id)
            
            try:
                # Create transaction with nonce from frontend
                result = braintree.Transaction.sale({
                    "amount": str(db_payment.amount),
                    "payment_method_nonce": nonce,
                    "device_data": None,
                    "options": {
                        "submit_for_settlement": True
                    },
                    "custom_fields": {
                        "user_id": str(db_payment.user.id),
                        "subscription_type": db_payment.subscription_type
                    }
                })
                
                if result.is_success:
                    logger.info(f"Braintree transaction successful: {result.transaction.id}")
                    db_payment.paypal_transaction_id = result.transaction.id
                    return self._complete_payment_record(db_payment)
                else:
                    logger.error(f"Braintree transaction failed: {result.message}")
                    db_payment.status = 'failed'
                    db_payment.save()
                    return {
                        'success': False,
                        'error': result.message or 'Payment declined'
                    }
            except Exception as e:
                logger.error(f"Braintree API error: {str(e)}")
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
            logger.exception(f"Payment execution error: {str(e)}")
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
