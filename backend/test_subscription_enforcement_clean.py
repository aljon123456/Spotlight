#!/usr/bin/env python
"""Test subscription tier enforcement in parking assignment engine."""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spotlight_project.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from parking_app.models import ParkingSlot, ParkingLot, Schedule, Assignment, Building, Campus
from parking_app.assignment_engine import ParkingAssignmentEngine
from users_app.models import Subscription

User = get_user_model()

def cleanup_test_data():
    """Clean up test data"""
    print("Cleaning up test data...")
    Assignment.objects.filter(user__email='test_subscription@example.com').delete()
    User.objects.filter(email='test_subscription@example.com').delete()

def setup_test_user(subscription_type=None):
    """Create a test user with optional subscription"""
    User.objects.filter(email='test_subscription@example.com').delete()
    
    user = User.objects.create_user(
        username='test_subscription',
        email='test_subscription@example.com',
        password='testpass123'
    )
    
    if subscription_type:
        Subscription.objects.filter(user=user).delete()
        Subscription.objects.create(
            user=user,
            subscription_type=subscription_type,
            status='active',
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=30),
            price=10.00,
            is_auto_renew=False
        )
        print(f"[OK] Created user with {subscription_type.upper()} subscription")
    else:
        print("[OK] Created user with NO subscription (BASIC tier)")
    
    return user

def create_test_slots():
    """Create test parking slots"""
    print("\nCreating test parking slots...")
    
    campus, _ = Campus.objects.get_or_create(
        name='Test Campus',
        defaults={'zip_code': '12345', 'total_parking_slots': 1000}
    )
    
    building, _ = Building.objects.get_or_create(
        campus=campus,
        code='TEST',
        defaults={'name': 'Test Building', 'description': 'Test'}
    )
    
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
    
    ParkingSlot.objects.filter(parking_lot=lot).delete()
    
    for slot_type in ['premium', 'reserved', 'regular']:
        for i in range(5):
            ParkingSlot.objects.get_or_create(
                parking_lot=lot,
                slot_number=f'{slot_type[0].upper()}{i:03d}',
                defaults={'slot_type': slot_type, 'status': 'available'}
            )
    
    print("[OK] Created test slots")

def create_test_schedule():
    """Create a test schedule"""
    campus, _ = Campus.objects.get_or_create(
        name='Test Campus',
        defaults={'zip_code': '12345', 'total_parking_slots': 1000}
    )
    
    building, _ = Building.objects.get_or_create(
        campus=campus,
        code='TEST',
        defaults={'name': 'Test Building', 'description': 'Test'}
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
    return schedule

def test_vip_slot_access():
    """Test VIP users get premium/reserved slots only"""
    print("\n" + "="*60)
    print("TEST 1: VIP User - Premium/Reserved Slots Only")
    print("="*60)
    
    user = setup_test_user('vip')
    engine = ParkingAssignmentEngine()
    schedule = create_test_schedule()
    available = engine._get_available_slots(user, schedule)
    
    slot_types = set(available.values_list('slot_type', flat=True))
    print(f"Available slot types for VIP: {slot_types}")
    
    if slot_types == {'premium', 'reserved'}:
        print("[PASS] VIP correctly restricted")
        return True
    else:
        print(f"[FAIL] Expected premium+reserved, got {slot_types}")
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
    print(f"Available slot types for Premium: {slot_types}")
    
    if slot_types == {'premium', 'regular'}:
        print("[PASS] Premium correctly restricted")
        return True
    else:
        print(f"[FAIL] Expected premium+regular, got {slot_types}")
        return False

def test_basic_slot_access():
    """Test Basic users get regular slots only"""
    print("\n" + "="*60)
    print("TEST 3: Basic User - Regular Slots Only")
    print("="*60)
    
    user = setup_test_user(None)
    engine = ParkingAssignmentEngine()
    schedule = create_test_schedule()
    available = engine._get_available_slots(user, schedule)
    
    slot_types = set(available.values_list('slot_type', flat=True))
    print(f"Available slot types for Basic: {slot_types}")
    
    if slot_types == {'regular'}:
        print("[PASS] Basic correctly restricted")
        return True
    else:
        print(f"[FAIL] Expected regular only, got {slot_types}")
        return False

def test_max_active_reservations():
    """Test max active reservation limits"""
    print("\n" + "="*60)
    print("TEST 4: Max Active Reservations Enforcement")
    print("="*60)
    
    cleanup_test_data()
    
    print("\n>>> Testing BASIC user (max 1 active)...")
    user = setup_test_user(None)
    schedule = create_test_schedule()
    engine = ParkingAssignmentEngine()
    
    assignment1 = engine.assign_parking(user, schedule)
    if assignment1:
        print(f"  [OK] First assignment created")
    else:
        print(f"  [ERROR] First assignment failed")
        return False
    
    campus, _ = Campus.objects.get_or_create(
        name='Test Campus',
        defaults={'zip_code': '12345', 'total_parking_slots': 1000}
    )
    building, _ = Building.objects.get_or_create(
        campus=campus,
        code='TEST',
        defaults={'name': 'Test Building', 'description': 'Test'}
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
        print(f"  [PASS] Second assignment blocked")
        return True
    else:
        print(f"  [FAIL] Second assignment should be blocked")
        return False

def test_subscription_scoring_boost():
    """Test subscription tier scoring boost"""
    print("\n" + "="*60)
    print("TEST 5: Subscription Tier Scoring Boost")
    print("="*60)
    
    user = setup_test_user('vip')
    engine = ParkingAssignmentEngine()
    
    reserved_slot = ParkingSlot.objects.filter(slot_type='reserved').first()
    if not reserved_slot:
        print("[ERROR] No reserved slots")
        return False
    
    schedule = create_test_schedule()
    score = engine._score_slot_enhanced(user, reserved_slot, schedule)
    
    basic_user = setup_test_user(None)
    basic_score = engine._score_slot_enhanced(basic_user, reserved_slot, schedule)
    
    print(f"VIP score: {score:.3f}, BASIC score: {basic_score:.3f}")
    
    if score > basic_score:
        print("[PASS] VIP scoring boost applied")
        return True
    else:
        print("[FAIL] VIP should score higher")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("SUBSCRIPTION TIER ENFORCEMENT TEST SUITE")
    print("="*60)
    
    create_test_slots()
    
    results = [
        ("VIP Slot Access", test_vip_slot_access()),
        ("Premium Slot Access", test_premium_slot_access()),
        ("Basic Slot Access", test_basic_slot_access()),
        ("Max Active Reservations", test_max_active_reservations()),
        ("Subscription Scoring Boost", test_subscription_scoring_boost()),
    ]
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All subscription enforcement tests PASSED!")
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed")
    
    cleanup_test_data()

if __name__ == '__main__':
    main()
