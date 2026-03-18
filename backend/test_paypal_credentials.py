#!/usr/bin/env python
"""
Test PayPal credentials and API connectivity
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spotlight_project.settings')
django.setup()

import paypalrestsdk
from django.conf import settings

print("=" * 60)
print("PayPal Configuration Test")
print("=" * 60)

# Check if credentials are loaded
print(f"\n✓ Mode: {settings.PAYPAL_MODE}")
print(f"✓ Client ID length: {len(settings.PAYPAL_CLIENT_ID)} chars")
print(f"✓ Client Secret length: {len(settings.PAYPAL_CLIENT_SECRET)} chars")

# Initialize PayPal SDK
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET,
})

print("\n✓ PayPal SDK configured")

# Test API
print("\n" + "=" * 60)
print("Testing PayPal API Connection")
print("=" * 60)

try:
    # Create a test payment (don't approve it)
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
                    "name": "Test Subscription",
                    "sku": "TEST-001",
                    "price": "5.00",
                    "currency": "USD",
                    "quantity": 1
                }]
            },
            "amount": {
                "total": "5.00",
                "currency": "USD",
                "details": {
                    "subtotal": "5.00"
                }
            },
            "description": "Test Payment"
        }]
    })
    
    if payment.create():
        print("✅ PayPal API Connection: SUCCESS")
        print(f"\n✓ Test Payment Created:")
        print(f"  - Payment ID: {payment.id}")
        print(f"  - State: {payment.state}")
        
        # Get approval URL
        for link in payment.links:
            if link.rel == "approval_url":
                print(f"  - Approval URL: {link.href[:50]}...")
                break
    else:
        print("❌ PayPal API Connection: FAILED")
        print(f"\n✗ Error: {payment.error}")
        
        # Print detailed error info
        if hasattr(payment, 'error'):
            print(f"\n✗ Detailed Error:")
            import json
            try:
                error_dict = json.loads(str(payment.error)) if isinstance(payment.error, str) else payment.error
                print(json.dumps(error_dict, indent=2))
            except:
                print(str(payment.error))

except Exception as e:
    print("❌ PayPal API Connection: ERROR")
    print(f"\n✗ Exception: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)
