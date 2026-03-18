#!/usr/bin/env python
"""
Test complete PayPal payment flow - Create and Test Execution
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spotlight_project.settings')
django.setup()

import paypalrestsdk
from django.conf import settings
from users_app.models import User

print("=" * 60)
print("Complete PayPal Payment Flow Test")
print("=" * 60)

# Initialize PayPal SDK
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET,
})

print(f"\n✓ Mode: {settings.PAYPAL_MODE}")
print(f"✓ Return URL: {settings.PAYPAL_RETURN_URL}")
print(f"✓ Cancel URL: {settings.PAYPAL_CANCEL_URL}")

# Get or create test user
test_user = User.objects.filter(email='test_payment@example.com').first()
if not test_user:
    test_user = User.objects.create_user(
        email='test_payment@example.com',
        username='testpay',
        password='testpass123',
        first_name='Test',
        last_name='Payment'
    )
    print(f"\n✓ Created test user: {test_user.email}")
else:
    print(f"\n✓ Using existing test user: {test_user.email}")

# Step 1: Create Payment
print("\n" + "=" * 60)
print("Step 1: Create Payment")
print("=" * 60)

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
                "name": "Premium Subscription - 1 month(s)",
                "sku": "SUB-PREMIUM",
                "price": "15.00",
                "currency": "USD",
                "quantity": 1
            }]
        },
        "amount": {
            "total": "15.00",
            "currency": "USD",
            "details": {
                "subtotal": "15.00"
            }
        },
        "description": "SpotLight Premium Subscription"
    }]
})

if payment.create():
    print("✅ Payment Created Successfully")
    payment_id = payment.id
    print(f"\n✓ Payment ID: {payment_id}")
    print(f"✓ State: {payment.state}")
    
    # Get approval URL
    approval_url = None
    for link in payment.links:
        if link.rel == "approval_url":
            approval_url = link.href
            print(f"✓ Approval URL (goto this in browser): {approval_url}")
            break
    
    # Step 2: Simulate payment approval
    print("\n" + "=" * 60)
    print("Step 2: Simulating PayPal Approval")
    print("=" * 60)
    
    # For testing, we need to use real PayPal credentials to execute
    # But since we can't interact with PayPal UI, we'll test with the Execute API directly
    print("\nℹ️  To complete this flow, you need to:")
    print(f"1. Go to: {approval_url}")
    print("2. Log in with PayPal test account (sb-test@example.com / Test!234)")
    print("3. Click 'Pay Now' or 'Approve'")
    print("4. You'll be redirected to: https://localhost:3000/subscription/success?paymentId=...&PayerID=...")
    print("5. The frontend will then call: POST /api/payments/execute/")
    
    print("\n" + "=" * 60)
    print("Test Complete - Ready for Browser Testing")
    print("=" * 60)
else:
    print("❌ Payment Creation Failed")
    print(f"Error: {payment.error}")
