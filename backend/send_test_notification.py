"""
Test script: Send notification from admin to user 'shanks'
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spotlight_project.settings')
django.setup()

from users_app.models import User
from parking_app.models import Notification

# Get or create shanks user
shanks, created = User.objects.get_or_create(
    username='shanks',
    defaults={
        'email': 'shanks@test.com',
        'first_name': 'Shanks',
        'last_name': 'User',
        'user_type': 'student'
    }
)

print("="*60)
print("📤 SENDING NOTIFICATION TO USER")
print("="*60)
print(f"\n✓ User: {shanks.username} ({shanks.email})")

# Admin sends notification
notification = Notification.objects.create(
    user=shanks,
    title='🚨 Parking Slot Unavailable',
    message='Your parking slot A-001 in Main Lot A has been changed to unavailable due to maintenance. Please book another slot.',
    notification_type='change',
    priority='high'
)

print(f"\n✓ Notification Sent!")
print(f"  - To: {shanks.username}")
print(f"  - Title: {notification.title}")
print(f"  - Message: {notification.message}")
print(f"  - Priority: {notification.priority}")
print(f"  - ID: {notification.id}")

print("\n" + "="*60)
print("✅ WHAT HAPPENS NEXT:")
print("="*60)
print("\n1. Go to: http://localhost:3000/notifications")
print("2. Login as: shanks / (set password)")
print("3. Watch the page...")
print("4. Within 5 seconds, the new notification appears! 🔔")

print("\n" + "="*60 + "\n")
