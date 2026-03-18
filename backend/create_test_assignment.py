#!/usr/bin/env python
"""Create test assignment data for admin user"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spotlight_project.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from users_app.models import User
from parking_app.models import (
    Campus, Building, ParkingLot, ParkingSlot, 
    Schedule, Assignment
)

# Get admin user
admin_user = User.objects.filter(username='admin').first()
if not admin_user:
    print("Admin user not found!")
else:
    # Get or create test campus/building/lot
    campus, _ = Campus.objects.get_or_create(name="Test Campus")
    building, _ = Building.objects.get_or_create(
        campus=campus,
        code="TEST",
        defaults={
            'name': "Test Building"
        }
    )
    lot, _ = ParkingLot.objects.get_or_create(
        campus=campus,
        name="Test Lot",
        defaults={
            'surface_type': 'outdoor',
            'total_slots': 100,
            'available_slots': 50,
            'nearest_building': building
        }
    )
    
    # Get or create a parking slot
    slot, _ = ParkingSlot.objects.get_or_create(
        parking_lot=lot,
        slot_number="A-001",
        defaults={
            'slot_type': 'regular',
            'status': 'available'
        }
    )
    
    # Get or create a schedule
    schedule, _ = Schedule.objects.get_or_create(
        user=admin_user,
        building=building,
        defaults={
            'start_date': timezone.now().date(),
            'end_date': (timezone.now() + timedelta(days=30)).date(),
            'start_time': '08:00:00',
            'end_time': '17:00:00'
        }
    )
    
    # Create or update assignment
    now = timezone.now()
    assignment, created = Assignment.objects.update_or_create(
        user=admin_user,
        schedule=schedule,
        defaults={
            'parking_slot': slot,
            'status': 'active',
            'start_datetime': now,
            'end_datetime': now + timedelta(hours=8),
            'ai_confidence_score': 0.95
        }
    )
    
    if created:
        print("✓ Test assignment created!")
    else:
        print("✓ Test assignment updated!")
    
    print(f"  Slot: {slot.slot_number}")
    print(f"  User: {admin_user.email}")
    print(f"  Status: {assignment.status}")
