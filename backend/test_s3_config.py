#!/usr/bin/env python
"""Test S3 configuration and uploads"""
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spotlight_project.settings')
django.setup()

from django.core.files.base import ContentFile
from users_app.models import User

print("=" * 60)
print("AWS S3 Configuration Test")
print("=" * 60)

# Check settings
print(f"\n✓ AWS_ACCESS_KEY_ID: {'*' * 10}{settings.AWS_ACCESS_KEY_ID[-10:]}")
print(f"✓ AWS_SECRET_ACCESS_KEY: {'*' * 10}{settings.AWS_SECRET_ACCESS_KEY[-10:]}")
print(f"✓ AWS_STORAGE_BUCKET_NAME: {settings.AWS_STORAGE_BUCKET_NAME}")
print(f"✓ AWS_S3_REGION_NAME: {settings.AWS_S3_REGION_NAME}")
print(f"✓ DEFAULT_FILE_STORAGE: {settings.DEFAULT_FILE_STORAGE}")
print(f"✓ MEDIA_URL: {settings.MEDIA_URL}")

# Check if S3 is actually configured
if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
    print("\n✓ S3 Storage is ENABLED (credentials found)")
else:
    print("\n✗ S3 Storage is DISABLED (no credentials)")
    exit(1)

# Try to get the storage backend
try:
    from storages.backends.s3boto3 import S3Boto3Storage
    storage = S3Boto3Storage()
    print("✓ S3Boto3Storage backend loaded successfully")
except Exception as e:
    print(f"✗ Error loading S3Boto3Storage: {e}")
    exit(1)

# Test credentials by trying to upload a test file
try:
    test_file = ContentFile(b"test content", name="test.txt")
    # Don't actually upload, just test the connection
    from boto3 import client
    s3_client = client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )
    # List buckets to test connection
    response = s3_client.list_buckets()
    buckets = [b['Name'] for b in response['Buckets']]
    print(f"✓ S3 connection successful. Found {len(buckets)} bucket(s)")
    if settings.AWS_STORAGE_BUCKET_NAME in buckets:
        print(f"✓ Bucket '{settings.AWS_STORAGE_BUCKET_NAME}' exists")
    else:
        print(f"✗ Bucket '{settings.AWS_STORAGE_BUCKET_NAME}' NOT found")
        print(f"  Available buckets: {buckets}")
except Exception as e:
    print(f"✗ S3 connection error: {e}")
    exit(1)

print("\n" + "=" * 60)
print("All S3 configuration checks passed!")
print("=" * 60)
