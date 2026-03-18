// Payment Cancel Page
import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import './PaymentPages.css';

function PaymentCancelPage() {
  const navigate = useNavigate();

  useEffect(() => {
    // Clear pending payment
    localStorage.removeItem('pending_payment_id');
    toast.warning('Payment cancelled. You can try again anytime.');
  }, []);

  return (
    <div className="payment-page cancel-page">
      <div className="payment-status">
        <div className="cancel-icon">✕</div>
        <h2>Payment Cancelled</h2>
        <p>Your payment was not completed.</p>
        <div className="action-buttons">
          <button 
            className="btn-primary"
            onClick={() => navigate('/subscription')}
          >
            Back to Subscription Plans
          </button>
          <button 
            className="btn-secondary"
            onClick={() => navigate('/dashboard')}
          >
            Go to Dashboard
          </button>
        </div>
      </div>
    </div>
  );
}

export default PaymentCancelPage;
