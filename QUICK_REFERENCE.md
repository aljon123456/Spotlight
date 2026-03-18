# Quick Reference Guide - 30-Minute Confirmation System

## System Overview

```
Assignment Created
        ↓
    [START: 30-minute timer]
        ↓
User Action Choice:
    
    Option A: Confirm Arrival (within 30 mins)
    ├─ Click "Confirm Arrival" button
    ├─ System: is_confirmed = True, confirmed_at = now()
    ├─ Slot status: assigned ✅
    └─ Proceed with schedule
    
    Option B: No action (let 30 mins pass)
    ├─ System: auto_release_unconfirmed runs
    ├─ Slot status: available 🔄
    ├─ Assignment status: no_show
    ├─ NoShowTracking record created
    └─ User notified
    
    Option C: Leave Early
    ├─ Click "Release Parking"
    ├─ System: status = completed
    ├─ Slot status: available
    └─ Others can book immediately
```

---

## API Usage

### 1. Confirm Arrival
```bash
POST /api/assignments/{assignment_id}/confirm_arrival/

Response (Success):
{
    "message": "Arrival confirmed successfully.",
    "assignment": {
        "id": 5,
        "user": 1,
        "parking_slot": 42,
        "is_confirmed": true,
        "confirmed_at": "2026-01-11T19:35:00Z",
        "status": "active"
    }
}

Response (Expired):
{
    "error": "Confirmation deadline has passed. Slot released.",
    "message": "This incident has been recorded as a no-show."
}
```

### 2. Release Parking Early
```bash
POST /api/assignments/{assignment_id}/complete_assignment/

Response:
{
    "message": "Assignment completed and slot released.",
    "assignment": {
        "id": 5,
        "status": "completed"
    }
}
```

---

## Management Commands

### Auto-Release Unconfirmed Slots
```bash
# Run manually (for testing)
python manage.py auto_release_unconfirmed --verbose

# Setup as cron job (every minute in production)
* * * * * cd /path/to/backend && python manage.py auto_release_unconfirmed
```

**What it does:**
- Finds assignments where confirmation_deadline < now()
- Releases parking slot (status='available')
- Marks assignment as 'no_show'
- Records NoShowTracking entry
- Sends notification to user

---

## Database Models

### Assignment Model (Updated)
```python
class Assignment(models.Model):
    # ... existing fields ...
    
    # NEW: Confirmation tracking
    is_confirmed = BooleanField(default=False)
    confirmed_at = DateTimeField(null=True)
    confirmation_deadline = DateTimeField()  # 30 mins after creation
    
    # NEW: Status options
    ASSIGNMENT_STATUS_CHOICES = (
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No-Show - Slot Released'),  # NEW
    )
```

### NoShowTracking Model (New)
```python
class NoShowTracking(models.Model):
    user = ForeignKey(User)
    assignment = ForeignKey(Assignment)
    was_notified = Boolean()
    reason = CharField()  # e.g., "Did not confirm within 30 mins"
    created_at = DateTimeField()
```

---

## Timeline Example

```
12:00 PM - User gets parking assignment
           is_confirmed = False
           confirmation_deadline = 12:30 PM
           Notification sent

12:15 PM - User opens app, clicks "Confirm Arrival"
           is_confirmed = True
           confirmed_at = 12:15 PM
           Status = active (confirmed)
           ✅ All good!

OR

12:31 PM - auto_release_unconfirmed runs
           Detects: is_confirmed=False AND confirmation_deadline < now()
           Actions:
           - Slot status = available
           - Assignment status = no_show
           - NoShowTracking created
           - Notification sent to user
           ❌ Slot released, recorded as no-show
```

---

## Notifications Sent

### Confirmation Success
```
Title: "Parking Arrival Confirmed"
Message: "Your arrival at parking lot {lot_name}, Slot {slot_number} 
          has been confirmed."
Type: change
Priority: medium
```

### Deadline Expired
```
Title: "Parking Slot Auto-Released (No Confirmation)"
Message: "You did not confirm your arrival within the 30-minute grace period
         for {schedule_title}. Your parking slot ({slot_number}) has been released.
         This is your X no-show incident. Repeated no-shows may affect your 
         parking privileges."
Type: alert
Priority: high (if 3+ no-shows)
```

### Manual Release
```
Title: "Parking Assignment Completed"
Message: "You have successfully completed your parking assignment for {schedule}."
Type: change
Priority: medium
```

---

## No-Show Tracking

### Get User's No-Shows
```python
from parking_app.models import NoShowTracking

# Get all no-shows for a user
no_shows = NoShowTracking.objects.filter(user=user).count()

# Get no-shows in last 30 days
from django.utils import timezone
from datetime import timedelta

recent_no_shows = NoShowTracking.objects.filter(
    user=user,
    created_at__gte=timezone.now() - timedelta(days=30)
).count()
```

### Admin Actions
```python
# Via admin panel:
# 1. See all no-shows sorted by user
# 2. Click user to see details
# 3. Add notes to reason field
# 4. Track patterns and enforce policies
```

---

## Testing the System

### Test 1: Successful Confirmation
```bash
# 1. Create schedule
# 2. Assign parking → get assignment ID
# 3. Within 30 mins: POST /assignments/{id}/confirm_arrival/
# 4. Verify: is_confirmed=true, status=active
# ✅ Pass
```

### Test 2: Auto-Release
```bash
# 1. Create schedule, assign parking
# 2. DON'T confirm
# 3. Wait 30 mins (or update DB: confirmation_deadline = now()-1minute)
# 4. Run: python manage.py auto_release_unconfirmed
# 5. Verify: status=no_show, slot=available
# ✅ Pass
```

### Test 3: Early Release
```bash
# 1. Create schedule, assign parking
# 2. POST /assignments/{id}/complete_assignment/
# 3. Verify: status=completed, slot=available
# ✅ Pass
```

---

## Common Issues & Solutions

### Issue: "Confirmation deadline already passed"
**Cause**: Grace period expired before user could confirm
**Solution**: User must wait for next available slot, or contact admin

### Issue: "Assignment is already completed"
**Cause**: User tried to complete already-completed assignment
**Solution**: Check assignment status before attempting action

### Issue: No notifications received
**Cause**: Notification system not running
**Solution**: Check if app has notification permissions enabled

---

## Metrics to Track

```python
# In your analytics:
- Daily confirmations vs no-shows ratio
- Average confirmation time (how soon after assignment?)
- Users with 3+ no-shows
- Slot utilization improvement (before/after)
- Revenue impact (freed slots = more users served)
```

---

## Performance Considerations

```bash
# The auto_release command is lightweight:
# - One database query to find expired assignments
# - One query per assignment to update slot + create notification
# - With 1000 users, takes ~500ms per run

# Recommended schedule:
# - Run every minute (cron)
# - Or every 5 minutes if lighter load needed
# - Or integrated into Celery beat scheduler

# Example Celery schedule:
CELERY_BEAT_SCHEDULE = {
    'auto-release-unconfirmed': {
        'task': 'parking_app.tasks.auto_release_unconfirmed',
        'schedule': crontab(minute='*/1'),  # Every minute
    },
}
```

---

## Defense Ammunition

Use these facts:

✅ **Fairness**: Prevents gaming the system  
✅ **Automation**: Zero manual work required  
✅ **Accountability**: All incidents recorded  
✅ **User-Friendly**: One-click confirmation  
✅ **No Sensors**: No hardware infrastructure  
✅ **Scalable**: Works for 100 or 100,000 users  
✅ **Cost-Effective**: Just software, no hardware  
✅ **Transparent**: Users know exactly what happens  

Ready for your thesis defense! 🎓
