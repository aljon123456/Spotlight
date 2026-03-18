#!/usr/bin/env python
"""
Test script to verify subscription tier enforcement in parking assignment engine.

Tests:
1. VIP users restricted to premium/reserved slots only
2. Premium users restricted to premium/regular slots only
3. Basic users restricted to regular slots only
4. Max active reservations enforced (Basic: 1, Premium: 3, VIP: 5)
5. Subscription tier scoring boost applied
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spotlight_project.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from parking_app.models import (
    ParkingSlot, ParkingLot, Schedule, Assignment, Building, Campus
)
from parking_app.assignment_engine import ParkingAssignmentEngine
from users_app.models import Subscription
from users_app.payment_models import PaymentPackage

User = get_user_model()

def cleanup_test_data():
    """Clean up test data before/after tests"""
    print("Cleaning up test data...")
    Assignment.objects.filter(user__email='test_subscription@example.com').delete()
    User.objects.filter(email='test_subscription@example.com').delete()

def setup_test_user(subscription_type=None):
    """Create a test user with optional subscription"""
    # Delete existing test user
    User.objects.filter(email='test_subscription@example.com').delete()
    
    user = User.objects.create_user(
        username='test_subscription',
        email='test_subscription@example.com',
        password='testpass123'
    )
    
    if subscription_type:
        # Get or create package
        package, _ = PaymentPackage.objects.get_or_create(
            subscription_type=subscription_type,
            defaults={
                'monthly_price': 10.00,
                'annual_price': 100.00,
                'features': 'Test features',
                'max_active_reservations': 5 if subscription_type == 'vip' else (3 if subscription_type == 'premium' else 1),
                'priority_slot_access': subscription_type == 'premium',
                'reserved_spots': subscription_type == 'vip'
            }
        )
        
        # Create subscription
        Subscription.objects.filter(user=user).delete()
        subscription = Subscription.objects.create(
            user=user,
            subscription_type=subscription_type,
            status='active',
            start_date=timezone.now(),
            expiry_date=timezone.now() + timedelta(days=30),
            payment_package=package
        )
        print(f"[OK] Created user with {subscription_type.upper()} subscription")
    else:
        print("[OK] Created user with NO subscription (BASIC tier)")
    
    return user

def create_test_slots():
    """Create test parking slots of different types"""
    print("\nCreating test parking slots...")
    
    # Create or get campus
    campus, _ = Campus.objects.get_or_create(
        name='Test Campus',
        defaults={'zip_code': '12345', 'total_parking_slots': 1000}
    )
    
    # Create or get building
    building, _ = Building.objects.get_or_create(
        campus=campus,
        code='TEST',
        defaults={'name': 'Test Building', 'description': 'Test building for testing'}
    )
    
    # Create or get parking lot
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
    
    # Clear existing test slots
    ParkingSlot.objects.filter(parking_lot=lot).delete()
    
    slot_types = ['premium', 'reserved', 'regular']
    quantity = 5
    
    for slot_type in slot_types:
        for i in range(quantity):
            slot, created = ParkingSlot.objects.get_or_create(
                parking_lot=lot,
                slot_number=f'{slot_type[0].upper()}{i:03d}',
                defaults={
                    'slot_type': slot_type,
                    'status': 'available'
                }
            )
            if created:
                print(f"  [OK] Created {slot_type} slot: {slot.slot_number}")

def create_test_schedule():
    """Create a test schedule"""
    print("\nCreating test schedule...")
    
    # Get or create campus and building
    campus, _ = Campus.objects.get_or_create(
        name='Test Campus',
        defaults={'zip_code': '12345', 'total_parking_slots': 1000}
    )
    
    building, _ = Building.objects.get_or_create(
        campus=campus,
        code='TEST',
        defaults={'name': 'Test Building', 'description': 'Test building for testing'}
    )
    
    start_time = timezone.now().time()
    end_time = (timezone.now() + timedelta(hours=2)).time()
    
    schedule, _ = Schedule.objects.get_or_create(
        start_date=timezone.now().date() + timedelta(days=1),
        start_time=start_time,
        defaults={
            'end_date': timezone.now().date() + timedelta(days=1),
            'end_time': end_time,
            'building': building
        }
    )
    print(f"[OK] Created schedule for {schedule.start_date}")
    return schedule

def test_vip_slot_access():
    """Test VIP users are restricted to premium/reserved slots only"""
    print("\n" + "="*60)
    print("TEST 1: VIP User - Premium/Reserved Slots Only")
    print("="*60)
    
    user = setup_test_user('vip')
    engine = ParkingAssignmentEngine()
    
    # Get available slots for VIP user
    schedule = create_test_schedule()
    available = engine._get_available_slots(user, schedule)
    
    slot_types = set(available.values_list('slot_type', flat=True))
    print(f"Available slot types for VIP user: {slot_types}")
    
    # Verify VIP only gets premium/reserved
    expected = {'premium', 'reserved'}
    if slot_types == expected:
        print(f"[PASS] VIP correctly restricted to {expected}")
        return True
    else:
        print(f"[FAIL] Expected {expected}, got {slot_types}")
        return False

def test_premium_slot_access():
    """Test Premium users get premium/regular slots"""
    print("\n" + "="*60)
    print("TEST 2: Premium User - Premium/Regular Slots Only")
    print("="*60)
    
    user = setup_test_user('premium')
    engine = ParkingAssignmentEngine()
    
    schedule = create_test_schedule()
    available = engine._get_available_slots(user, schedule)
    
    slot_types = set(available.values_list('slot_type', flat=True))
    print(f"Available slot types for Premium user: {slot_types}")
    
    expected = {'premium', 'regular'}
    if slot_types == expected:
        print(f"[PASS] Premium correctly restricted to {expected}")
        return True
    else:
        print(f"[FAIL] Expected {expected}, got {slot_types}")
        return False

def test_basic_slot_access():
    """Test Basic users only get regular slots"""
    print("\n" + "="*60)
    print("TEST 3: Basic User (No Subscription) - Regular Slots Only")
    print("="*60)
    
    user = setup_test_user(None)  # No subscription = BASIC
    engine = ParkingAssignmentEngine()
    
    schedule = create_test_schedule()
    available = engine._get_available_slots(user, schedule)
    
    slot_types = set(available.values_list('slot_type', flat=True))
    print(f"Available slot types for Basic user: {slot_types}")
    
    expected = {'regular'}
    if slot_types == expected:
        print(f"[PASS] Basic correctly restricted to {expected}")
        return True
    else:
        print(f"[FAIL] Expected {expected}, got {slot_types}")
        return False

def test_max_active_reservations():
    """Test max active reservation limits are enforced"""
    print("\n" + "="*60)
    print("TEST 4: Max Active Reservations Enforcement")
    print("="*60)
    
    cleanup_test_data()
    
    # Test BASIC user can only have 1 active
    print("\n>>> Testing BASIC user (max 1 active)...")
    user = setup_test_user(None)
    schedule = create_test_schedule()
    engine = ParkingAssignmentEngine()
    
    # Create first assignment
    assignment1 = engine.assign_parking(user, schedule)
    if assignment1:
        print(f"  [OK] First assignment created: {assignment1.parking_slot.slot_number}")
    else:
        print(f"  [ERROR] First assignment failed")
        return False
    
    # Try to create second assignment (should fail for BASIC)
    campus, _ = Campus.objects.get_or_create(
        name='Test Campus',
        defaults={'zip_code': '12345', 'total_parking_slots': 1000}
    )
    building, _ = Building.objects.get_or_create(
        campus=campus,
        code='TEST',
        defaults={'name': 'Test Building', 'description': 'Test building for testing'}
    )
    schedule2 = Schedule.objects.create(
        start_date=timezone.now().date() + timedelta(days=2),
        start_time=timezone.now().time(),
        end_date=timezone.now().date() + timedelta(days=2),
        end_time=(timezone.now() + timedelta(hours=2)).time(),
        building=building
    )
    
    assignment2 = engine.assign_parking(user, schedule2)
    if assignment2 is None:
        print(f"  [PASS] Second assignment blocked (BASIC max = 1)")
        return True
    else:
        print(f"  [FAIL] Second assignment should be blocked but was created: {assignment2.parking_slot.slot_number}")
        return False

def test_subscription_scoring_boost():
    """Test subscription tier scoring boost is applied"""
    print("\n" + "="*60)
    print("TEST 5: Subscription Tier Scoring Boost")
    print("="*60)
    
    user = setup_test_user('vip')
    engine = ParkingAssignmentEngine()
    
    # Get a reserved slot
    reserved_slot = ParkingSlot.objects.filter(slot_type='reserved').first()
    if not reserved_slot:
        print(f"  [ERROR] No reserved slots available for testing"
        return False
    
    schedule = create_test_schedule()
    
    # Score the reserved slot for VIP user
    score = engine._score_slot_enhanced(user, reserved_slot, schedule)
    print(f"Score for VIP user + reserved slot: {score:.3f}")
    
    # Score the same slot for basic user (should be lower or 0)
    basic_user = setup_test_user(None)
    basic_score = engine._score_slot_enhanced(basic_user, reserved_slot, schedule)
    print(f"Score for BASIC user + reserved slot: {basic_score:.3f}")
    
    if score > basic_score:
        print(f"[PASS] VIP scoring boost applied ({score:.3f} > {basic_score:.3f})")
        return True
    else:
        print(f"[FAIL] VIP should score higher for reserved slots")
        return False

def main():
    """Run all subscription enforcement tests"""
    print("\n" + "="*60)
    print("SUBSCRIPTION TIER ENFORCEMENT TEST SUITE")
    print("="*60)
    
    # Create test data
    create_test_slots()
    
    # Run tests
    results = []
    results.append(("VIP Slot Access", test_vip_slot_access()))
    results.append(("Premium Slot Access", test_premium_slot_access()))
    results.append(("Basic Slot Access", test_basic_slot_access()))
    results.append(("Max Active Reservations", test_max_active_reservations()))
    results.append(("Subscription Scoring Boost", test_subscription_scoring_boost()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[PASS]" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All subscription enforcement tests PASSED!")
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed")
    
    # Cleanup
    cleanup_test_data()

if __name__ == '__main__':
    main()
