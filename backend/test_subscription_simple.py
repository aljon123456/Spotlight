#!/usr/bin/env python
"""Simple test of subscription tier enforcement."""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spotlight_project.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from parking_app.models import ParkingSlot, ParkingLot, Schedule, Building, Campus
from users_app.models import Subscription

User = get_user_model()

def test_subscription_enforcement():
    """Test subscription tier filtering"""
    print("\n" + "="*60)
    print("SUBSCRIPTION TIER ENFORCEMENT TEST")
    print("="*60)
    
    # Create test campus and building
    campus, _ = Campus.objects.get_or_create(
        name='Test Campus',
        defaults={'zip_code': '12345', 'total_parking_slots': 1000}
    )
    
    building, _ = Building.objects.get_or_create(
        campus=campus,
        code='TEST',
        defaults={'name': 'Test Building', 'description': 'Test'}
    )
    
    # Create test lot and slots
    lot, _ = ParkingLot.objects.get_or_create(
        name='Test Lot',
        defaults={
            'campus': campus,
            'total_slots': 100,
            'available_slots': 100,
            'surface_type': 'outdoor',
            'nearest_building': building
        }
    )
    
    # Create slots of each type
    ParkingSlot.objects.all().delete()  # Delete all slots
    lot.refresh_from_db()
    lot.available_slots = 100
    lot.save()
    
    slot_counter = 0
    for slot_type in ['premium', 'reserved', 'regular']:
        for i in range(3):
            ParkingSlot.objects.create(
                parking_lot=lot,
                slot_number=f'SLOT{slot_counter:04d}',
                slot_type=slot_type,
                status='available'
            )
            slot_counter += 1
    
    print("[OK] Created test parking slots and environment")
    
    # Create test users
    User.objects.filter(email__in=['vip@test.com', 'premium@test.com', 'basic@test.com']).delete()
    
    vip_user = User.objects.create_user(email='vip@test.com', username='vip_user', password='pass')
    premium_user = User.objects.create_user(email='premium@test.com', username='prem_user', password='pass')
    basic_user = User.objects.create_user(email='basic@test.com', username='basic_user', password='pass')
    
    # Create VIP subscription
    Subscription.objects.filter(user=vip_user).delete()
    Subscription.objects.create(
        user=vip_user,
        subscription_type='vip',
        status='active',
        end_date=timezone.now() + timedelta(days=30),
        price=30.00
    )
    
    # Create Premium subscription
    Subscription.objects.filter(user=premium_user).delete()
    Subscription.objects.create(
        user=premium_user,
        subscription_type='premium',
        status='active',
        end_date=timezone.now() + timedelta(days=30),
        price=15.00
    )
    
    # Basic user has no subscription
    print("[OK] Created test users with subscriptions")
    
    # Create a test schedule for one user
    schedule = Schedule.objects.create(
        user=vip_user,
        schedule_type='class',
        title='Test Schedule',
        building=building,
        start_time='09:00:00',
        end_time='11:00:00',
        days_of_week='Monday,Wednesday,Friday',
        start_date=timezone.now().date(),
        end_date=timezone.now().date() + timedelta(days=30)
    )
    print("[OK] Created test schedule")
    
    # Now test the assignment engine's slot filtering
    from parking_app.assignment_engine import ParkingAssignmentEngine
    engine = ParkingAssignmentEngine()
    
    # Test VIP user
    print("\n[TEST 1] VIP User Slot Access")
    vip_slots = engine._get_available_slots(vip_user, schedule)
    vip_types = set(vip_slots.values_list('slot_type', flat=True))
    print(f"Available for VIP: {vip_types}")
    vip_pass = vip_types == {'premium', 'reserved'}
    if vip_pass:
        print("[PASS] VIP gets premium+reserved")
    else:
        print(f"[FAIL] Expected premium+reserved, got {vip_types}")
    
    # Test Premium user
    print("\n[TEST 2] Premium User Slot Access")
    premium_slots = engine._get_available_slots(premium_user, schedule)
    premium_types = set(premium_slots.values_list('slot_type', flat=True))
    print(f"Available for Premium: {premium_types}")
    premium_pass = premium_types == {'premium', 'regular'}
    if premium_pass:
        print("[PASS] Premium gets premium+regular")
    else:
        print(f"[FAIL] Expected premium+regular, got {premium_types}")
    
    # Test Basic user
    print("\n[TEST 3] Basic User Slot Access")
    basic_slots = engine._get_available_slots(basic_user, schedule)
    basic_types = set(basic_slots.values_list('slot_type', flat=True))
    print(f"Available for Basic: {basic_types}")
    basic_pass = basic_types == {'regular'}
    if basic_pass:
        print("[PASS] Basic gets regular only")
    else:
        print(f"[FAIL] Expected regular only, got {basic_types}")
    
    # Summary
    print("\n" + "="*60)
    results = [vip_pass, premium_pass, basic_pass]
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"[SUCCESS] All tests passed ({passed}/{total})")
    else:
        print(f"[WARNING] {total - passed} test(s) failed")
    
    print("="*60)
    
    # Cleanup
    print("\nCleaning up test data...")
    User.objects.filter(email__in=['vip@test.com', 'premium@test.com', 'basic@test.com']).delete()

if __name__ == '__main__':
    test_subscription_enforcement()
