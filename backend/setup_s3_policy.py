#!/usr/bin/env python
"""
Script to create a bucket policy that makes profile_pictures public
"""
import boto3
import json
from django.conf import settings
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spotlight_project.settings')
django.setup()

print("=" * 60)
print("Setting up S3 Bucket Policy for Public Access")
print("=" * 60)

s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_S3_REGION_NAME
)

bucket_name = settings.AWS_STORAGE_BUCKET_NAME

# Policy to make profile_pictures public
bucket_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": f"arn:aws:s3:::{bucket_name}/profile_pictures/*"
        },
        {
            "Sid": "PublicReadDocuments",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": f"arn:aws:s3:::{bucket_name}/documents/*"
        }
    ]
}

try:
    s3_client.put_bucket_policy(
        Bucket=bucket_name,
        Policy=json.dumps(bucket_policy)
    )
    print(f"✓ Bucket policy applied successfully!")
    print(f"✓ Profile pictures are now publicly accessible")
    print(f"✓ Bucket: {bucket_name}")
except Exception as e:
    print(f"✗ Error setting bucket policy: {e}")
    
# List current objects
print(f"\nListing objects in bucket...")
try:
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix='profile_pictures/')
    if 'Contents' in response:
        print(f"✓ Found {len(response['Contents'])} profile picture(s)")
        for obj in response['Contents']:
            url = f"https://{bucket_name}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{obj['Key']}"
            print(f"  - {obj['Key']}")
            print(f"    URL: {url}")
    else:
        print("✗ No profile pictures found in bucket")
except Exception as e:
    print(f"✗ Error listing objects: {e}")

print("\n" + "=" * 60)
