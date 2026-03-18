# 💳 PayPal Integration Setup Guide

## ✅ What Was Created

### **Backend Setup**
1. ✅ **Payment Models** (`payment_models.py`)
   - `Payment` - Stores PayPal transaction records
   - `PaymentPackage` - Stores subscription pricing

2. ✅ **PayPal Service** (`paypal_service.py`)
   - Payment creation
   - Payment execution
   - Subscription creation

3. ✅ **Payment API Endpoints** (`payment_views.py`)
   - `/api/payment-packages/` - List subscription packages
   - `/api/payments/initiate/` - Start payment
   - `/api/payments/execute/` - Complete payment
   - `/api/payments/cancel/` - Cancel payment
   - `/api/subscription/current/` - Get current subscription

4. ✅ **Database Models**
   - Added to Django admin interface
   - Ready for migrations

---

## 🔧 Setup Instructions

### **Step 1: Install PayPal SDK**
```bash
cd backend
pip install paypalrestsdk
```

### **Step 2: Create and Upload PayPal Credentials**

1. Go to https://developer.paypal.com/
2. Log in or create account
3. Create a **Sandbox** app for testing:
   - **App ID** → Copy to `PAYPAL_CLIENT_ID`
   - **Secret** → Copy to `PAYPAL_CLIENT_SECRET`

4. Update `.env` file:
```env
PAYPAL_MODE=sandbox
PAYPAL_CLIENT_ID=your_client_id_here
PAYPAL_CLIENT_SECRET=your_client_secret_here
PAYPAL_RETURN_URL=http://localhost:3000/subscription/success
PAYPAL_CANCEL_URL=http://localhost:3000/subscription/cancel
```

### **Step 3: Create Database Migrations**
```bash
cd backend

# Create migration for payment models
python manage.py makemigrations users_app

# Apply migrations
python manage.py migrate
```

### **Step 4: Create Payment Packages (Initial Setup)**

Use Django admin to add subscription packages:
```
Admin URL: http://localhost:8000/admin
Navigate to: Payment Packages → Add

Examples to create:

✅ Basic
  - Monthly: $5
  - Annual: $50
  - Features: Standard parking, 1 reservation

✅ Premium
  - Monthly: $15
  - Annual: $150
  - Features: Priority parking, 3 reservations, priority queue

✅ VIP
  - Monthly: $30
  - Annual: $300
  - Features: Reserved spots, 5 reservations, premium support
```

Or run this Django shell command:
```bash
python manage.py shell
```

Then paste:
```python
from users_app.payment_models import PaymentPackage

PackagePayment.objects.create(
    subscription_type='basic',
    monthly_price=5.00,
    annual_price=50.00,
    features='Standard parking, 1 active reservation',
    max_active_reservations=1,
    priority_slot_access=False,
    reserved_spots=False
)

PaymentPackage.objects.create(
    subscription_type='premium',
    monthly_price=15.00,
    annual_price=150.00,
    features='Priority parking, 3 active reservations, priority queue',
    max_active_reservations=3,
    priority_slot_access=True,
    reserved_spots=False
)

PaymentPackage.objects.create(
    subscription_type='vip',
    monthly_price=30.00,
    annual_price=300.00,
    features='Reserved spots, 5 active reservations, premium support',
    max_active_reservations=5,
    priority_slot_access=True,
    reserved_spots=True
)
```

---

## 📱 Frontend Integration (React)

Create a new page: `SubscriptionPage.js`
```jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';

function SubscriptionPage({ user }) {
  const [packages, setPackages] = useState([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    // Fetch available packages
    fetch('http://localhost:8000/api/payment-packages/')
      .then(r => r.json())
      .then(data => setPackages(data.results || data))
      .catch(err => console.error(err));
  }, []);

  const handleSubscribe = async (subscriptionType, months) => {
    setLoading(true);
    try {
      // Initiate payment
      const response = await fetch('http://localhost:8000/api/payments/initiate/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          subscription_type: subscriptionType,
          duration_months: months
        })
      });

      const data = await response.json();
      
      if (data.success) {
        // Redirect to PayPal
        window.location.href = data.approval_url;
      } else {
        toast.error(data.error);
      }
    } catch (error) {
      toast.error('Failed to initiate payment');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="subscription-container">
      <h1>🎓 Choose Your Parking Plan</h1>
      
      <div className="packages-grid">
        {packages.map(pkg => (
          <div key={pkg.subscription_type} className="package-card">
            <h2>{pkg.subscription_type.toUpperCase()}</h2>
            <p className="price">${pkg.monthly_price}/month</p>
            <p className="annual-price">${pkg.annual_price}/year</p>
            
            <ul className="features">
              {pkg.features_list.map(f => (
                <li key={f}>✓ {f}</li>
              ))}
            </ul>
            
            <div className="buttons">
              <button 
                onClick={() => handleSubscribe(pkg.subscription_type, 1)}
                disabled={loading}
              >
                Buy Monthly
              </button>
              <button 
                onClick={() => handleSubscribe(pkg.subscription_type, 12)}
                disabled={loading}
              >
                Buy Yearly
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default SubscriptionPage;
```

---

## 🔄 Payment Flow

```
1. User clicks "Buy" → Subscription Page
2. Select package & duration
3. Click "Subscribe"
4. Backend initiates PayPal payment
5. User redirected to PayPal to approve
6. User approves and returns
7. Backend executes payment
8. Subscription created in database
9. User gets access to premium features
```

---

## 🧪 Testing with PayPal Sandbox

**Sandbox Buyer Account:**
```
Email: sb-xxxxxx@personal.example.com
Password: 12345678
```
(Get from PayPal Developer Dashboard)

---

## 📋 API Endpoints Reference

### **1. List Available Packages**
```
GET /api/payment-packages/
Response:
{
  "results": [
    {
      "subscription_type": "basic",
      "monthly_price": "5.00",
      "annual_price": "50.00",
      "features": "...",
      "features_list": ["Feature 1", "Feature 2"]
    }
  ]
}
```

### **2. Initiate Payment**
```
POST /api/payments/initiate/
Body: {
  "subscription_type": "premium",
  "duration_months": 1
}
Response: {
  "success": true,
  "approval_url": "https://www.sandbox.paypal.com/...",
  "payment_id": 123
}
```

### **3. Execute Payment (called after PayPal approval)**
```
POST /api/payments/execute/
Body: {
  "paypal_payment_id": "PAYID-...",
  "payer_id": "...",
  "payment_id": 123
}
Response: {
  "success": true,
  "subscription_type": "premium"
}
```

### **4. Get Current Subscription**
```
GET /api/subscription/current/
Response: {
  "subscription_type": "premium",
  "status": "active",
  "start_date": "2026-03-18T...",
  "end_date": "2026-04-18T...",
  "price": "15.00"
}
```

---

## ✨ Next Steps

1. ✅ Install paypalrestsdk
2. ✅ Get PayPal API credentials
3. ✅ Update `.env` file
4. ✅ Run migrations
5. ✅ Create payment packages in admin
6. ✅ Add SubscriptionPage to frontend
7. ✅ Add cart/checkout UI

Ready to accept payments! 💰
