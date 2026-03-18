# Production Deployment Guide - Spotlight Parking System

## Quick Start (Render.com)
**Estimated Time: 15-20 minutes**

### Step 1: Prepare Your Code
```bash
# Ensure everything is committed
git status
git add -A
git commit -m "Production deployment ready"
git push origin main
```

### Step 2: Set Up Render Account
1. Go to https://render.com
2. Sign up with GitHub account
3. Connect your GitHub repository (aljon123456/Spotlight)

### Step 3: Create PostgreSQL Database
1. In Render dashboard, click "New +" → "PostgreSQL"
2. **Configuration:**
   - Name: `spotlight-db`
   - Database: `spotlight_db`
   - User: `postgres`
   - Region: Select closest to you
   - Plan: Free (or Starter for production)
3. Click "Create Database"
4. **Copy the Internal Database URL** (starts with `postgres://`)

### Step 4: Deploy Backend
1. Click "New +" → "Web Service"
2. **Configuration:**
   - **Name:** `spotlight-api`
   - **Environment:** Python 3
   - **Build Command:** 
     ```
     pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
     ```
   - **Start Command:** 
     ```
     gunicorn spotlight_project.wsgi:application --bind 0.0.0.0:10000
     ```
   - **Instance Type:** Free or Starter
   - **Region:** Same as database

3. Click "Create Web Service"

### Step 5: Configure Environment Variables
In Render dashboard for the backend service, go to **Environment** tab:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | Generate a django key: use any long random string or run `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `spotlight-api.onrender.com,yourdomain.com` |
| `DATABASE_URL` | Paste the PostgreSQL Internal URL from Step 3 |
| `CORS_ALLOWED_ORIGINS` | `https://spotlight-frontend.onrender.com,https://yourdomain.com` |
| `PAYPAL_MODE` | `sandbox` (or `live` when production-ready) |
| `PAYPAL_CLIENT_ID` | Your PayPal Client ID |
| `PAYPAL_CLIENT_SECRET` | Your PayPal Client Secret |
| `PAYPAL_RETURN_URL` | `https://spotlight-frontend.onrender.com/subscription/success` |
| `PAYPAL_CANCEL_URL` | `https://spotlight-frontend.onrender.com/subscription/cancel` |

### Step 6: Deploy Frontend
1. Click "New +" → "Web Service"
2. **Configuration:**
   - **Name:** `spotlight-frontend`
   - **Environment:** Node
   - **Build Command:** 
     ```
     npm install && npm run build
     ```
   - **Start Command:** 
     ```
     npm start
     ```
   - **Instance Type:** Free or Starter
   - **Region:** Same as backend

3. Go to **Environment** tab and add:

| Key | Value |
|-----|-------|
| `REACT_APP_API_URL` | `https://spotlight-api.onrender.com/api` |
| `REACT_APP_PAYPAL_CLIENT_ID` | Your PayPal Client ID |

### Step 7: Verify Deployment
1. Visit `https://spotlight-api.onrender.com/admin/` → Should see Django admin
2. Visit `https://spotlight-frontend.onrender.com/` → Should see login page
3. Try logging in with credentials
4. Test PayPal subscription flow (in sandbox mode)

---

## Production Checklist

### Security ✅
- [ ] Set `DEBUG=False` in production
- [ ] Update `SECRET_KEY` to a unique, long random string
- [ ] Configure `ALLOWED_HOSTS` for your domain
- [ ] Set `HTTPS` only (Render handles this)
- [ ] Configure CORS properly
- [ ] Review JWT token expiration times
- [ ] Enable CSRF protection (already enabled)

### Database ✅
- [ ] PostgreSQL database created and running
- [ ] Database migrations applied (`python manage.py migrate`)
- [ ] Backup strategy in place (Render PostgreSQL has automatic backups)
- [ ] Static files collected (`python manage.py collectstatic`)

### Email Notifications (Optional) ✅
- [ ] Configure email for password resets and notifications
- [ ] Get Gmail or SendGrid API credentials
- [ ] Add to environment variables

### PayPal Integration ✅
- [ ] Update `PAYPAL_RETURN_URL` to production domain
- [ ] Update `PAYPAL_CANCEL_URL` to production domain
- [ ] Test payment flow end-to-end
- [ ] When ready: Switch `PAYPAL_MODE` from `sandbox` to `live`
- [ ] Add production PayPal credentials

### Monitoring (Optional) ✅
- [ ] Set up error tracking (Sentry: https://sentry.io)
- [ ] Monitor application logs in Render dashboard
- [ ] Set up uptime monitoring

### Domain & DNS (Optional) ✅
- [ ] Purchase custom domain
- [ ] Update Render service with custom domain
- [ ] Configure DNS records
- [ ] SSL certificate (Render handles automatically)

---

## Production Settings (Backend)

### Update `settings.py` for Production
Ensure these settings are in place:

```python
# Security
DEBUG = config('DEBUG', default=False, cast=bool)
SECRET_KEY = config('SECRET_KEY')  # Must be set in production
ALLOWED_HOSTS = config('ALLOWED_HOSTS').split(',')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='spotlight_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Or use DATABASE_URL for Render
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600
    )
}

# CORS
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS').split(',')
CORS_ALLOW_CREDENTIALS = True

# Static Files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security Headers
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
X_FRAME_OPTIONS = 'DENY'
```

---

## Requirements for Production

### Backend (`requirements.txt`)
```
django==4.2.7
djangorestframework==3.14.0
django-cors-headers==4.0.0
python-decouple==3.8
Pillow==10.1.0
paypalrestsdk==1.13.3
psycopg2-binary==2.9.9
gunicorn==21.2.0
whitenoise==6.6.0
dj-database-url==2.1.0
```

### Frontend (`frontend/package.json`)
```json
{
  "name": "spotlight-frontend",
  "version": "1.0.0",
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.x.x"
  },
  "scripts": {
    "build": "react-scripts build"
  }
}
```

---

## Troubleshooting

### Backend won't start
```bash
# Check logs in Render dashboard
# Common issues:
# - Missing environment variables: Check environment section
# - Database connection: Verify DATABASE_URL is correct
# - Migration failed: Check Render logs for details
```

### Frontend can't connect to API
```javascript
// Check in browser console (F12)
// Verify REACT_APP_API_URL points to correct backend
// Check CORS headers response
// Ensure backend CORS_ALLOWED_ORIGINS includes frontend domain
```

### PayPal sandbox not working
```
- Ensure PAYPAL_MODE=sandbox
- Verify credentials in .env are correct
- Check return/cancel URLs match configuration
```

---

## After Deployment

### 1. Create Admin User
```bash
# SSH into backend in Render, or use Django admin
python manage.py createsuperuser
# Username: admin
# Email: your@email.com
# Password: Strong password

# Then visit: https://your-api-domain.com/admin/
```

### 2. Verify Features
- [ ] User registration and login
- [ ] Profile creation and updates
- [ ] Schedule creation
- [ ] Parking assignment (test with different subscription tiers)
- [ ] PayPal payment flow (sandbox)
- [ ] Subscription display on profile

### 3. Load Sample Data (Optional)
```bash
python manage.py populate_data  # Uses management command
```

### 4. Monitor & Maintain
- Check application logs regularly
- Monitor database usage
- Set up error alerts
- Plan regular backups

---

## Custom Domain Setup

### Using Render + Custom Domain
1. In Render dashboard, go to service settings
2. Add **Custom Domain**
3. Update DNS records at your domain registrar:
   - Add CNAME record pointing to Render URL

### SSL Certificate
- Render automatically provisions SSL via Let's Encrypt
- Redirects HTTP to HTTPS automatically

---

## Cost Estimates (Render.com)

| Service | Free Tier | Starter |
|---------|-----------|---------|
| Backend (Web) | $0 (spins down) | $7/mo |
| Frontend (Web) | $0 (spins down) | $7/mo |
| PostgreSQL | $0 (limited) | $15/mo |
| **Total** | **$0** | **~$29/mo** |

### Recommendations:
- **Development**: Use Free tier
- **Production**: Use Starter for reliability
- **Scale Up**: Use Standard/Pro if traffic increases

---

## Support & Resources

- **Render Docs**: https://render.com/docs
- **Django Docs**: https://docs.djangoproject.com
- **React Docs**: https://react.dev
- **PayPal API**: https://developer.paypal.com/docs

---

**Last Updated**: March 18, 2026
**Status**: Ready for Production Deployment ✅
