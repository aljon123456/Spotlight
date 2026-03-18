// Subscription Page component - Purchase parking plans
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import './SubscriptionPage.css';

function SubscriptionPage({ user }) {
  const [packages, setPackages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedDuration, setSelectedDuration] = useState({}); // { basic: 1, premium: 1, vip: 1 }
  const navigate = useNavigate();

  useEffect(() => {
    // Fetch available packages
    fetch('http://localhost:8000/api/payment-packages/', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    })
      .then(r => r.json())
      .then(data => {
        setPackages(data.results || data);
        // Initialize duration selections
        const durations = {};
        (data.results || data).forEach(pkg => {
          durations[pkg.subscription_type] = 1;
        });
        setSelectedDuration(durations);
      })
      .catch(err => {
        console.error(err);
        toast.error('Failed to load packages');
      });
  }, []);

  const handleSubscribe = async (subscriptionType) => {
    setLoading(true);
    try {
      const duration = selectedDuration[subscriptionType] || 1;

      // Initiate payment
      const response = await fetch('http://localhost:8000/api/payments/initiate/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          subscription_type: subscriptionType,
          duration_months: parseInt(duration)
        })
      });

      const data = await response.json();

      if (data.success) {
        // Store payment ID for later verification
        localStorage.setItem('pending_payment_id', data.payment_id);
        // Redirect to PayPal
        window.location.href = data.approval_url;
      } else {
        toast.error(data.error || 'Failed to initiate payment');
      }
    } catch (error) {
      console.error('Payment error:', error);
      toast.error('Failed to initiate payment');
    } finally {
      setLoading(false);
    }
  };

  const handleDurationChange = (type, value) => {
    setSelectedDuration({
      ...selectedDuration,
      [type]: value
    });
  };

  const getPrice = (pkg, duration) => {
    if (duration === 12) {
      return parseFloat(pkg.annual_price);
    }
    return parseFloat(pkg.monthly_price);
  };

  return (
    <main className="subscription-container">
      <div className="subscription-header">
        <h1>🎓 Choose Your Parking Plan</h1>
        <p>Unlock premium parking features and guaranteed spot availability</p>
      </div>

      <div className="packages-grid">
        {packages.map(pkg => (
          <div key={pkg.subscription_type} className={`package-card ${pkg.subscription_type}`}>
            {pkg.subscription_type === 'vip' && <div className="badge">⭐ MOST POPULAR</div>}

            <h2 className="package-name">{pkg.subscription_type.toUpperCase()}</h2>

            <div className="duration-selector">
              <label>Duration:</label>
              <select
                value={selectedDuration[pkg.subscription_type] || 1}
                onChange={(e) => handleDurationChange(pkg.subscription_type, e.target.value)}
              >
                <option value="1">Monthly</option>
                <option value="12">Yearly (Save 17%)</option>
              </select>
            </div>

            <div className="price-section">
              <div className="price">
                ${getPrice(pkg, selectedDuration[pkg.subscription_type] || 1).toFixed(2)}
              </div>
              <div className="price-period">
                {selectedDuration[pkg.subscription_type] === 12 ? 'per year' : 'per month'}
              </div>
            </div>

            <ul className="features-list">
              {pkg.features_list && pkg.features_list.map((feature, idx) => (
                <li key={idx}>
                  <span className="checkmark">✓</span>
                  {feature.trim()}
                </li>
              ))}
            </ul>

            <div className="benefits">
              <p className="benefit-item">
                <span className="icon">👥</span>
                {pkg.max_active_reservations} Active Reservation{pkg.max_active_reservations > 1 ? 's' : ''}
              </p>
              {pkg.priority_slot_access && (
                <p className="benefit-item">
                  <span className="icon">⚡</span>
                  Priority Slot Access
                </p>
              )}
              {pkg.reserved_spots && (
                <p className="benefit-item">
                  <span className="icon">🔐</span>
                  Reserved Parking Spots
                </p>
              )}
            </div>

            <button
              className={`btn-subscribe ${loading ? 'loading' : ''}`}
              onClick={() => handleSubscribe(pkg.subscription_type)}
              disabled={loading}
            >
              {loading ? 'Processing...' : 'Choose Plan'}
            </button>
          </div>
        ))}
      </div>

      <div className="comparison-table">
        <h3>📊 Feature Comparison</h3>
        <table>
          <thead>
            <tr>
              <th>Feature</th>
              <th>Basic</th>
              <th>Premium</th>
              <th>VIP</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Active Reservations</td>
              <td>1</td>
              <td>3</td>
              <td>5</td>
            </tr>
            <tr>
              <td>Priority Queue Access</td>
              <td>❌</td>
              <td>✅</td>
              <td>✅</td>
            </tr>
            <tr>
              <td>Reserved Spots</td>
              <td>❌</td>
              <td>❌</td>
              <td>✅</td>
            </tr>
            <tr>
              <td>Priority Support</td>
              <td>❌</td>
              <td>❌</td>
              <td>✅</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div className="faq-section">
        <h3>❓ FAQ</h3>
        <div className="faq-item">
          <h4>Can I change my plan later?</h4>
          <p>Yes! You can upgrade or downgrade your plan at any time from your profile.</p>
        </div>
        <div className="faq-item">
          <h4>Is there a refund policy?</h4>
          <p>Yes, we offer a 7-day money-back guarantee if you're not satisfied.</p>
        </div>
        <div className="faq-item">
          <h4>Do you offer discounts for longer terms?</h4>
          <p>Yes! Purchase a yearly plan and save 17% compared to monthly billing.</p>
        </div>
      </div>
    </main>
  );
}

export default SubscriptionPage;
