"""
Test script to demonstrate the confirmation system.
Run this to see the confirmation flow.
"""
import os
import django
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spotlight_project.settings')
django.setup()

from users_app.models import User
from parking_app.models import Campus, Building, ParkingLot, ParkingSlot, Schedule, Assignment

print("\n" + "="*60)
print("🅿️  PARKING CONFIRMATION SYSTEM TEST")
print("="*60 + "\n")

# Get or create test user
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={'email': 'test@example.com', 'first_name': 'Test', 'last_name': 'User', 'user_type': 'student'}
)
print(f"✓ User: {user.username} ({user.email})")

# Get or create campus/building/lot/slot
campus, _ = Campus.objects.get_or_create(name='Main Campus', defaults={'city': 'Boston', 'state': 'MA'})
building, _ = Building.objects.get_or_create(name='Science Building', defaults={'campus': campus, 'code': 'SCI'})
lot, _ = ParkingLot.objects.get_or_create(name='Main Lot A', defaults={'campus': campus, 'surface_type': 'asphalt', 'total_slots': 100, 'available_slots': 100})
slot, _ = ParkingSlot.objects.get_or_create(
    parking_lot=lot,
    slot_number='A-001',
    defaults={'status': 'available', 'slot_type': 'standard'}
)
print(f"✓ Parking Slot: {slot.parking_lot.name} - {slot.slot_number} (Status: {slot.status})")

# Create a schedule
from datetime import date, timedelta

today = date.today()
schedule = Schedule.objects.create(
    user=user,
    title='CS 101 Lecture',
    schedule_type='class',
    building=building,
    days_of_week='Monday,Wednesday,Friday',
    start_time='09:00:00',
    end_time='10:00:00',
    start_date=today,
    end_date=today + timedelta(days=120)
)
print(f"✓ Schedule: {schedule.title} ({schedule.days_of_week} {schedule.start_time}-{schedule.end_time})")

# Create an assignment (unconfirmed)
now = timezone.now()
assignment = Assignment.objects.create(
    user=user,
    parking_slot=slot,
    schedule=schedule,
    start_datetime=now + timedelta(hours=1),
    end_datetime=now + timedelta(hours=2),
    status='active',
    is_confirmed=False,
    confirmation_deadline=now + timedelta(minutes=30)
)
print(f"\n✓ Assignment Created: ID={assignment.id}")
print(f"  - Status: {assignment.status}")
print(f"  - is_confirmed: {assignment.is_confirmed}")
print(f"  - Confirmation Deadline: {assignment.confirmation_deadline}")
print(f"  - Parking Slot: {slot.slot_number} (Status: {slot.status})")

print("\n" + "-"*60)
print("📋 TEST SCENARIO 1: User Confirms Arrival (WITHIN 30 mins)")
print("-"*60)

# Simulate user confirming
assignment.is_confirmed = True
assignment.confirmed_at = timezone.now()
assignment.save()

print(f"✓ Confirmation Recorded!")
print(f"  - is_confirmed: {assignment.is_confirmed}")
print(f"  - confirmed_at: {assignment.confirmed_at}")
print(f"  - Status: {assignment.status} (Active - User can keep parking)")

print("\n" + "-"*60)
print("📋 TEST SCENARIO 2: User DOESN'T Confirm (AFTER 30 mins)")
print("-"*60)

# Create another assignment for no-show test
slot2, _ = ParkingSlot.objects.get_or_create(
    parking_lot=lot,
    slot_number='A-002',
    defaults={'status': 'available', 'slot_type': 'standard'}
)

assignment2 = Assignment.objects.create(
    user=user,
    parking_slot=slot2,
    schedule=schedule,
    start_datetime=now + timedelta(hours=1),
    end_datetime=now + timedelta(hours=2),
    status='active',
    is_confirmed=False,
    confirmation_deadline=now - timedelta(minutes=1)  # Already expired!
)

print(f"✓ Assignment Created: ID={assignment2.id}")
print(f"  - is_confirmed: {assignment2.is_confirmed}")
print(f"  - confirmation_deadline: {assignment2.confirmation_deadline} (EXPIRED!)")
print(f"  - Parking Slot: {slot2.slot_number} (Status: {slot2.status})")

print("\n  Running: python manage.py auto_release_unconfirmed\n")

# Simulate the auto-release command
from parking_app.models import NoShowTracking, Notification

expired = Assignment.objects.filter(
    status='active',
    is_confirmed=False,
    confirmation_deadline__lt=timezone.now()
)

for assign in expired:
    # Release slot
    assign.parking_slot.status = 'available'
    assign.parking_slot.save()
    
    # Mark no-show
    assign.status = 'no_show'
    assign.save()
    
    # Record no-show
    NoShowTracking.objects.create(
        user=assign.user,
        assignment=assign,
        reason="Did not confirm arrival within 30-minute grace period"
    )
    
    # Notify user
    Notification.objects.create(
        user=assign.user,
        title='Parking Slot Auto-Released',
        message='Your parking slot was released because confirmation deadline passed.',
        priority='high'
    )
    
    print(f"✓ Released slot {assign.parking_slot.slot_number}")
    print(f"  - Assignment Status: {assign.status}")
    print(f"  - Parking Slot Status: {assign.parking_slot.status}")

print("\n" + "="*60)
print("✅ TEST COMPLETE!")
print("="*60)
print(f"\nTo confirm arrival via API:")
print(f"  POST /api/assignments/{assignment.id}/confirm_arrival/")
print(f"\nTo see more details:")
print(f"  - Check database: SELECT * FROM parking_app_assignment;")
print(f"  - Check no-shows: SELECT * FROM parking_app_noshowtracking;")
print(f"\n" + "="*60 + "\n")
