"""
Script to create payment packages in the database.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spotlight_project.settings')
django.setup()

from users_app.payment_models import PaymentPackage

# Create Basic Package
PaymentPackage.objects.get_or_create(
    subscription_type='basic',
    defaults={
        'monthly_price': 5.00,
        'annual_price': 50.00,
        'features': 'Standard parking, 1 active reservation',
        'max_active_reservations': 1,
        'priority_slot_access': False,
        'reserved_spots': False,
        'is_active': True
    }
)
print("✓ Basic package created")

# Create Premium Package
PaymentPackage.objects.get_or_create(
    subscription_type='premium',
    defaults={
        'monthly_price': 15.00,
        'annual_price': 150.00,
        'features': 'Priority parking, 3 active reservations, priority queue',
        'max_active_reservations': 3,
        'priority_slot_access': True,
        'reserved_spots': False,
        'is_active': True
    }
)
print("✓ Premium package created")

# Create VIP Package
PaymentPackage.objects.get_or_create(
    subscription_type='vip',
    defaults={
        'monthly_price': 30.00,
        'annual_price': 300.00,
        'features': 'Reserved spots, 5 active reservations, premium support',
        'max_active_reservations': 5,
        'priority_slot_access': True,
        'reserved_spots': True,
        'is_active': True
    }
)
print("✓ VIP package created")

print("\n✅ All payment packages created successfully!")
print("\nPackages:")
for pkg in PaymentPackage.objects.all():
    print(f"  - {pkg.subscription_type.upper()}: ${pkg.monthly_price}/month, ${pkg.annual_price}/year")
