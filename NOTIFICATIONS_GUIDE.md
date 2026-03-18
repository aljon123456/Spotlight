# 🔔 How Notifications Work - Admin to User

## **The System Flow**

```
ADMIN (You at localhost:8000/admin)
    ↓
Creates/Sends Notification
    ↓
Notification saved in Database
    ↓
USER (At localhost:3000)
    ↓
Frontend auto-refreshes every 5 seconds
    ↓
User sees new notification! 🎉
```

---

## **Step-by-Step: Send Notification & See It**

### **Step 1: Create a User to Notify**
Go to Django Admin: `http://localhost:8000/admin`
- Username: `admin`
- Password: `admin123`

Add a new User or use existing one:
- Username: `shanks` (or any user)
- Email: `shanks@test.com`
- User Type: `student`

---

### **Step 2: Send Notification from Admin**

In Django Admin, go to **Notifications** and click **Add Notification**

Fill in:
- **User**: Select "shanks"
- **Title**: "🚨 Parking Slot Unavailable"
- **Message**: "Your parking slot has been changed to unavailable due to maintenance"
- **Notification Type**: Select "change"
- **Priority**: Select "high"
- **Is Read**: Unchecked (so user sees it as NEW)

Click **SAVE**

---

### **Step 3: User Sees Notification**

1. Login to Frontend as that user: `http://localhost:3000`
   - Username: `shanks`
   - Password: (whatever you set)

2. Go to **Notifications page** (`http://localhost:3000/notifications`)
   - **AUTO-REFRESHES every 5 seconds** ✨
   - You'll see the new notification appear!

3. Or check **Dashboard**
   - **Unread Notifications** counter updates automatically

---

## **Where Notifications Show**

| Location | Updates | Real-Time? |
|----------|---------|-----------|
| `/notifications` page | Every 5 seconds | ✅ Yes (auto-refresh) |
| `/dashboard` (counter) | Every 5 seconds | ✅ Yes (auto-refresh) |
| Admin panel | Manual (F5 to refresh) | ❌ No |

---

## **API Behind the Scenes**

Frontend calls this API every 5 seconds:
```
GET /api/notifications/?is_read=false
```

This fetches all **unread notifications** for the logged-in user.

---

## **Example Notification Types**

- **assignment**: "You've been assigned parking slot A-45"
- **change**: "Your parking slot has been changed"
- **reminder**: "Your parking assignment ends in 1 hour"
- **alert**: "System maintenance scheduled"
- **offer**: "Better parking slot available for your schedule"

---

## **Priority Levels**

- 🔴 **urgent**: Red color, immediate action needed
- 🟠 **high**: Orange color, important
- 🟡 **medium**: Yellow color, regular info
- 🔵 **low**: Blue color, non-urgent

---

## **To Mark as Read**

User can click **"Mark as read"** button on each notification
- Or click **"Mark All as Read"** to mark everything

This updates `is_read = True` in database

---

## **Create Multiple Test Notifications**

Quick SQL to create test notifications:
```python
from parking_app.models import Notification
from users_app.models import User

user = User.objects.get(username='shanks')

# Create 3 notifications
for i in range(3):
    Notification.objects.create(
        user=user,
        title=f'Test Notification {i+1}',
        message=f'This is test notification number {i+1}',
        notification_type='alert',
        priority='high'
    )
```

---

## **Key Points**

✅ **Notifications save to database** - Persistent  
✅ **Frontend refreshes every 5 seconds** - Near real-time  
✅ **User sees updates on Notifications page** - Auto appears  
✅ **Dashboard shows unread count** - Updates automatically  
✅ **Admin can send/manage** - Full control  

---

## **Future Enhancement: Real WebSockets**

Currently using **polling** (refresh every 5 sec).

For instant notifications, could add **WebSockets**:
- Requires: Django Channels library
- Updates appear instantly instead of 5-second delay
- Better for production systems

---

**That's it! Your notification system is working!** 🎉
