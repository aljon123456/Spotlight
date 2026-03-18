// Payment Success Page
import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import './PaymentPages.css';

function PaymentSuccessPage({ setUser }) {
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // Get payment details from URL
    const paypalPaymentId = searchParams.get('paymentId');
    const payerId = searchParams.get('PayerID');
    const paymentId = localStorage.getItem('pending_payment_id');

    if (!paypalPaymentId || !payerId || !paymentId) {
      toast.error('Invalid payment details');
      setLoading(false);
      return;
    }

    // Execute payment
    executePayment(paypalPaymentId, payerId, paymentId);
  }, [searchParams]);

  const executePayment = async (paypalPaymentId, payerId, paymentId) => {
    try {
      console.log('Executing payment with:', { paypalPaymentId, payerId, paymentId });
      
      const response = await fetch('http://localhost:8000/api/payments/execute/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          paypal_payment_id: paypalPaymentId,
          payer_id: payerId,
          payment_id: paymentId
        })
      });

      console.log('Execute response status:', response.status);
      const data = await response.json();
      console.log('Execute response data:', data);

      if (data.success || response.ok) {
        // Clear pending payment
        localStorage.removeItem('pending_payment_id');
        
        // Refresh user data
        const profileResponse = await fetch('http://localhost:8000/api/auth/profile/', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        const userData = await profileResponse.json();
        setUser(userData);
        localStorage.setItem('user_data', JSON.stringify(userData));

        toast.success('Payment successful! Your subscription is now active.');
        setLoading(false);
        
        // Redirect to dashboard after 3 seconds
        setTimeout(() => {
          navigate('/dashboard');
        }, 3000);
      } else {
        const errorMsg = data.error || data.message || 'Payment failed for unknown reason';
        console.error('Payment execution error:', errorMsg);
        toast.error(errorMsg);
        setLoading(false);
        
        // Redirect to subscription page to retry
        setTimeout(() => {
          navigate('/subscription');
        }, 3000);
      }
    } catch (error) {
      console.error('Payment fetch error:', error);
      toast.error('Error processing payment: ' + error.message);
      setLoading(false);
    }
  };

  return (
    <div className="payment-page success-page">
      {loading ? (
        <div className="payment-status">
          <div className="spinner"></div>
          <h2>Processing Payment...</h2>
          <p>Please wait while we confirm your subscription.</p>
        </div>
      ) : (
        <div className="payment-status">
          <div className="success-icon">✓</div>
          <h2>Payment Successful!</h2>
          <p>Your subscription is now active.</p>
          <p className="redirect-text">Redirecting to dashboard...</p>
        </div>
      )}
    </div>
  );
}

export default PaymentSuccessPage;
