#!/usr/bin/env python
"""Test file upload endpoint"""
import os
import django
import requests
from io import BytesIO
from PIL import Image

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spotlight_project.settings')
django.setup()

from users_app.models import User
from rest_framework_simplejwt.tokens import RefreshToken

print("=" * 60)
print("File Upload Endpoint Test")
print("=" * 60)

# Get admin user and generate token
admin = User.objects.filter(username='admin').first()
if not admin:
    print("✗ Admin user not found")
    exit(1)

refresh = RefreshToken.for_user(admin)
access_token = str(refresh.access_token)
print(f"✓ Admin user found: {admin.username}")
print(f"✓ Generated access token: {access_token[:50]}...")

# Create a test image
test_image = Image.new('RGB', (100, 100), color='red')
image_io = BytesIO()
test_image.save(image_io, format='PNG')
image_io.seek(0)

# Test 1: Upload profile picture
print("\n[Test 1] Uploading profile picture...")
files = {'file': ('test_profile.png', image_io, 'image/png')}
headers = {'Authorization': f'Bearer {access_token}'}

response = requests.post(
    'http://localhost:8000/api/uploads/upload_profile_picture/',
    files=files,
    headers=headers
)

print(f"Response Status: {response.status_code}")
print(f"Response Body: {response.json()}")

if response.status_code == 200:
    print("✓ Profile picture uploaded successfully!")
    data = response.json()
    print(f"  URL: {data.get('url')}")
else:
    print(f"✗ Upload failed: {response.json()}")

print("\n" + "=" * 60)
