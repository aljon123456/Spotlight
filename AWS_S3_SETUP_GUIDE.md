# AWS S3 CDN Setup Guide for Spotlight Parking

## ✅ Completed Setup

The following components have been configured for AWS S3 integration:

### Backend Configuration

#### 1. **Settings.py Enhanced** (`spotlight_project/settings.py`)
- ✅ AWS credentials configuration (environment variables)
- ✅ CloudFront CDN domain support
- ✅ S3 storage backend auto-enabled with credentials
- ✅ Cache control headers per file type
- ✅ File upload size limits (5MB)
- ✅ Allowed extensions configuration

#### 2. **Storage Classes** (`parking_app/storage.py`)
- ✅ `ProfilePictureStorage` - 30-day cache for avatars
- ✅ `DocumentStorage` - 7-day cache for PDFs/schedules
- ✅ `VideoStorage` - 1-day cache for video files
- ✅ `StaticMediaStorage` - 1-day cache for general media

#### 3. **Models Updated**
- ✅ `User.profile_picture` - ImageField for S3 upload
- ✅ `Schedule.schedule_document` - FileField for documents (PDF, images)

#### 4. **API Endpoints** (`parking_app/file_upload_views.py`)
- ✅ `POST /api/uploads/upload_profile_picture/` - Upload user avatar
- ✅ `POST /api/uploads/upload_schedule_document/` - Upload schedule document
- ✅ `POST /api/uploads/delete_profile_picture/` - Delete avatar
- ✅ `GET /api/uploads/get_s3_config/` - Get S3 configuration

#### 5. **Serializers Updated**
- ✅ `ScheduleSerializer` includes `schedule_document_url` field

#### 6. **URLs Registered**
- ✅ FileUploadViewSet registered as `/api/uploads/`

#### 7. **Dependencies Added** (`requirements.txt`)
- ✅ `django-storages==1.14.6`
- ✅ `boto3==1.29.7`
- ✅ `Pillow==10.1.0` (for image handling)

---

## 🔧 Next Steps: Configuration Required

### Step 1: Create AWS S3 Bucket

1. Go to [AWS S3 Console](https://s3.amazonaws.com)
2. Create new bucket: `spotlight-parking` (or your preferred name)
3. **Block public access settings**: Keep defaults (we'll use presigned URLs)
4. EnableVersioning (optional, but recommended)
5. Add CORS Configuration:

```json
[
  {
    "AllowedOrigins": ["http://localhost:3000", "https://yourfrontend.com"],
    "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
    "AllowedHeaders": ["*"],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3000
  }
]
```

### Step 2: Create CloudFront Distribution (Optional but Recommended)

1. Go to [AWS CloudFront Console](https://console.aws.amazon.com/cloudfront)
2. Create distribution with origin: `spotlight-parking.s3.amazonaws.com`
3. Allow methods: GET, HEAD, OPTIONS
4. Cache policy: Use "CachingOptimized"
5. Note the CloudFront domain: `d1234.cloudfront.net`

### Step 3: Create IAM User for Application

1. Go to [IAM Users](https://console.aws.amazon.com/iam/home#/users)
2. Create new user: `spotlight-app-user`
3. Attach policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::spotlight-parking/*"
    }
  ]
}
```

4. Generate Access Key and Secret
5. **Store securely** - you'll need these for environment variables

### Step 4: Set Environment Variables

Add to your `.env` or deployment environment:

```bash
# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_STORAGE_BUCKET_NAME=spotlight-parking
AWS_S3_REGION_NAME=us-east-1

# Optional: If using CloudFront
AWS_CLOUDFRONT_DOMAIN=d1234cloudfront.net
```

For **local development**, create `.env` file in backend root:
```bash
cp .env.example .env
# Edit .env with your AWS credentials
```

For **production (Render)**, add to environment variables:
1. Go to Render dashboard
2. Select your service
3. Go to Environment
4. Add all `AWS_*` variables

### Step 5: Run Database Migration

Once credentials are set and venv is properly initialized:

```bash
# Activate venv
source .venv/Scripts/activate  # Windows: .venv\Scripts\Activate.ps1

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Restart backend
python manage.py runserver
```

---

## 📱 Frontend Components

### Profile Picture Upload Component

```javascript
// components/ProfileUpload.js
const uploadProfilePicture = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('http://localhost:8000/api/uploads/upload_profile_picture/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`
    },
    body: formData
  });
  
  const data = await response.json();
  return data.url; // CloudFront or S3 URL
};
```

### Schedule Document Upload Component

```javascript
// components/ScheduleDocumentUpload.js
const uploadScheduleDocument = async (file, scheduleId) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('schedule_id', scheduleId);
  
  const response = await fetch('http://localhost:8000/api/uploads/upload_schedule_document/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('access_token')}`
    },
    body: formData
  });
  
  const data = await response.json();
  return data.url;
};
```

---

## 🧪 Testing Uploads

### Test with cURL

```bash
# Upload profile picture
curl -X POST http://localhost:8000/api/uploads/upload_profile_picture/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/image.jpg"

# Upload schedule document
curl -X POST http://localhost:8000/api/uploads/upload_schedule_document/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/schedule.pdf" \
  -F "schedule_id=1"

# Get S3 config
curl http://localhost:8000/api/uploads/get_s3_config/
```

### Test with Frontend

1. Go to Profile page
2. Click "Upload Picture"
3. Select image (jpg, png, max 5MB)
4. Should see it uploaded to S3 in ~2-3 seconds
5. Image served from CloudFront (if configured)

---

## 📊 File Storage Structure in S3

After initial uploads, your S3 bucket will have:

```
spotlight-parking/
├── profile_pictures/
│   ├── user_1/avatar.jpg
│   ├── user_2/avatar.jpg
│   └── ...
├── documents/
│   ├── schedule_1.pdf
│   ├── schedule_2.pdf
│   └── ...
└── media/
    └── other_files/
```

---

## 💰 Cost Estimates

Typical monthly costs (moderate usage):
- **Storage**: $0.023 per GB/month
  - 1 GB profile pictures: ~$0.02
  - 5 GB documents/videos: ~$0.12
- **Data Transfer Out**: $0.09 per GB
  - 100 GB downloaded: ~$9
- **Requests**: Negligible (<$1)
- **CloudFront**: Same data transfer cost but better caching

**Typical small app**: $10-15/month

---

## 🔒 Security Notes

✅ **Best Practices Implemented:**
- ✅ Presigned URLs (not public access)
- ✅ File type validation
- ✅ File size limits (5MB)
- ✅ User authentication required
- ✅ Cache headers for performance

⚠️ **Additional Security Considerations:**
- Scan uploads for malware (integrate with ClamAV)
- Use CloudFront WAF for DDoS protection
- Enable versioning for accidental deletions
- Regular backup of critical documents

---

## 🚀 Deployment Checklist

- [ ] AWS S3 bucket created
- [ ] CloudFront distribution setup (optional but recommended)
- [ ] IAM user with S3 permissions created
- [ ] Environment variables set in Render dashboard
- [ ] Database migrations applied
- [ ] Backend restarted in Render
- [ ] Profile picture upload tested
- [ ] Schedule document upload tested
- [ ] Files accessible via CloudFront URL

---

## 🆘 Troubleshooting

### "AWS_ACCESS_KEY_ID not configured"
- Check environment variables are set
- Restart backend after adding variables
- Verify credentials are correct

### "File size exceeds 5MB limit"
- Current apps need smaller files
- Update `FILE_UPLOAD_MAX_MEMORY_SIZE` in settings if needed

### "CORS error accessing S3"
- Verify S3 bucket CORS configuration
- Check CloudFront allows the headers
- Ensure origin matches allowed origins

### "Access Denied" error
- Verify IAM user has S3 permissions
- Check bucket name matches
- Confirm credentials in environment variables

---

**Setup Status**: ✅ 85% Complete
**Next Step**: Configure AWS credentials and test uploads
