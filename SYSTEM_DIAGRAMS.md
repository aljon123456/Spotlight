# System Architecture Diagrams

## 1. User Confirmation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    PARKING ASSIGNMENT CREATED                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Assignment Fields:                                       │   │
│  │ - is_confirmed: False                                   │   │
│  │ - confirmed_at: null                                    │   │
│  │ - confirmation_deadline: now() + 30 mins               │   │
│  │ - status: 'active'                                      │   │
│  │ - parking_slot: assigned                                │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ↓
               ┌────────────────────────┐
               │   30-Minute Timer       │
               │   Starts Running        │
               │                         │
               │  User receives push     │
               │  notification + email   │
               └────────────────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
         ↓                  ↓                  ↓
    ┌────────┐         ┌────────┐        ┌──────────┐
    │ USER   │         │ NO      │        │ TIME     │
    │CONFIRMS│         │ACTION   │        │EXPIRES   │
    │ARRIVAL │         │(WAITS)  │        │          │
    └────────┘         └────────┘        └──────────┘
         │                  │                  │
         ↓                  ↓                  ↓
    ┌─────────────────────────────────────────────────┐
    │ is_confirmed = True              Auto-Release   │
    │ confirmed_at = now()             is_confirmed=F │
    │ Status: 'active'       ❌    Status: 'no_show' │
    │ ✅ User Can Proceed    │    ❌ Slot Released    │
    │                        │    ❌ No-Show Recorded │
    │                        ↓    ❌ Notification Sent│
    │                    USER NOTIFIED              │
    └─────────────────────────────────────────────────┘
```

---

## 2. Slot Status Lifecycle

```
┌─────────────┐
│  AVAILABLE  │ (Initial state - slot is free)
└──────┬──────┘
       │
       ├─ User creates schedule & requests parking
       ↓
┌──────────────┐
│   ASSIGNED   │ (Slot reserved for this user - 30 min confirmation)
└──────┬───────┘
       │
       ├─ User confirms within 30 mins ✅
       │  └─> ASSIGNED (confirmed - stays until schedule end)
       │      └─> (Schedule time ends or user releases)
       │          └─> AVAILABLE (released back)
       │
       ├─ User doesn't confirm within 30 mins ❌
       │  └─> AUTO-RELEASED
       │      └─> AVAILABLE (immediately freed for others)
       │
       ├─ Slot needs maintenance 🔧
       │  └─> MAINTENANCE
       │      └─> (after repair)
       │          └─> AVAILABLE
       │
       └─ Slot has obstruction or is blocked 🚫
          └─> BLOCKED
              └─> (once cleared)
                  └─> AVAILABLE
```

---

## 3. Database Relationships

```
┌──────────────────────────────────────────────────────────────┐
│                                                               │
│                          USER                                │
│  ┌─────────────────────────────────────────┐                │
│  │ id, username, email, vehicle_plate, ... │                │
│  └────────────────┬───────────────────────┘                │
│                   │                                          │
│     ┌─────────────┼─────────────┐                           │
│     │             │             │                           │
│     ↓             ↓             ↓                           │
│  SCHEDULE    ASSIGNMENT   NO_SHOW_TRACKING
│  (classes)   (parking)    (violations)
│             ┌─────────────────────────────────────┐         │
│             │ id                                  │         │
│             │ user_id (FK)                        │         │
│             │ parking_slot_id (FK) ──────────┐   │         │
│             │ schedule_id (FK)                │   │         │
│             │ is_confirmed                    │   │         │
│             │ confirmed_at                    │   │         │
│             │ confirmation_deadline           │   │         │
│             │ status                          │   │         │
│             │ start_datetime                  │   │         │
│             │ end_datetime                    │   │         │
│             └─────────────────────────────────┘   │         │
│                                                   │         │
│                            ┌──────────────────────┘         │
│                            ↓                                │
│                   PARKING_SLOT                             │
│          ┌──────────────────────────┐                      │
│          │ id                       │                      │
│          │ parking_lot_id (FK)      │                      │
│          │ slot_number              │                      │
│          │ status (assigned, etc)   │                      │
│          │ slot_type (premium, etc) │                      │
│          └──────────────┬───────────┘                      │
│                         │                                  │
│                         ↓                                  │
│                  PARKING_LOT                              │
│             ┌──────────────────────┐                      │
│             │ id                   │                      │
│             │ campus_id (FK)       │                      │
│             │ name, surface_type   │                      │
│             │ available_slots, ... │                      │
│             └──────────────────────┘                      │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

---

## 4. Confirmation Deadline Management

```
TIME AXIS:
─────────────────────────────────────────────────────────────────

0 min: Assignment Created
       ├─ is_confirmed = False
       ├─ confirmation_deadline = 00:30
       ├─ Notification sent to user
       └─ Timer starts

5 min: auto_release_unconfirmed runs (every 1 min)
       └─ Checks: is deadline < now()? NO → Continue

15 min: User opens app, clicks "Confirm Arrival"
        ├─ is_confirmed = True
        ├─ confirmed_at = 00:15
        └─ Status = active ✅

20 min: auto_release_unconfirmed runs
        └─ Checks: is_confirmed=True? YES → SKIP (don't release)

30 min: auto_release_unconfirmed runs
        └─ Checks: is deadline < now()? 
           ├─ If is_confirmed=True? SKIP (user confirmed)
           └─ If is_confirmed=False? RELEASE
              ├─ Slot status = available
              ├─ Assignment status = no_show
              ├─ NoShowTracking created
              └─ Notification sent to user ❌

31+ min: Slot is available
         └─ Other users can book it immediately
```

---

## 5. Automatic Release Process

```
AUTO_RELEASE_UNCONFIRMED Management Command

TRIGGERED: Every minute (via cron or Celery Beat)

STEPS:
1. Query database:
   SELECT * FROM Assignment 
   WHERE status='active' 
   AND is_confirmed=False 
   AND confirmation_deadline < NOW()

2. For each expired assignment:
   
   a) Release the parking slot:
      UPDATE ParkingSlot 
      SET status='available' 
      WHERE id=assignment.parking_slot_id
   
   b) Mark assignment as no-show:
      UPDATE Assignment 
      SET status='no_show' 
      WHERE id=assignment.id
   
   c) Create no-show record:
      INSERT INTO NoShowTracking 
      VALUES (user_id, assignment_id, reason, ...)
   
   d) Send notification:
      INSERT INTO Notification 
      VALUES (
        user_id,
        title='Parking Slot Auto-Released',
        message='...',
        priority='high',
        ...
      )
   
   e) Check no-show count:
      SELECT COUNT(*) FROM NoShowTracking 
      WHERE user_id=assignment.user_id
      
      IF count >= 5:
         LOG WARNING: User has too many no-shows

3. Output summary:
   "✓ Successfully auto-released 3 expired assignments"

DATABASE CHANGES:
Before:  Assignment(status='active', is_confirmed=False)
         Slot(status='assigned')
         
After:   Assignment(status='no_show', is_confirmed=False)
         Slot(status='available')
         NoShowTracking(user, assignment, reason)
         Notification(user, alert about no-show)
```

---

## 6. API Endpoint Flow

```
CLIENT REQUEST:
┌─────────────────────────────────────────┐
│ POST /api/assignments/{id}/confirm_arrival/
│ Headers: Authorization: Bearer {token}
└────────────────┬────────────────────────┘
                 │
                 ↓
BACKEND VALIDATION:
┌─────────────────────────────────────────┐
│ 1. Check authentication ✓               │
│ 2. Check permission (is it user's own?) │
│ 3. Check if already confirmed ✓         │
│ 4. Check if deadline passed             │
└────────────────┬────────────────────────┘
                 │
       ┌─────────┴─────────┐
       ↓                   ↓
   ✅ VALID          ❌ EXPIRED
   │                   │
   ↓                   ↓
UPDATE:          AUTO-RELEASE:
├─is_confirmed=T  ├─status='no_show'
├─confirmed_at=N  ├─Create NoShowTrack
├─status='active' ├─Send high-priority
└─Notification    │  notification
                  └─Response: 400 error
                     "Deadline passed"

                  ↓

RESPONSE 200:        RESPONSE 400:
┌──────────────┐    ┌──────────────────┐
│{             │    │{                 │
│ "message":   │    │ "error":         │
│ "Confirmed"  │    │ "Deadline passed"│
│ "assignment":│    │ "message":       │
│ {...}        │    │ "No-show issued" │
│}             │    │}                 │
└──────────────┘    └──────────────────┘
```

---

## 7. No-Show Escalation

```
User Behavior Tracking:

1st No-Show:
├─ Notification: "⚠️ You have 1 no-show"
├─ Priority: medium
├─ Action: None - just track
└─ User Can Still Book

2nd No-Show:
├─ Notification: "⚠️ You have 2 no-shows"
├─ Priority: medium
├─ Action: Monitor closely
└─ User Can Still Book

3rd No-Show:
├─ Notification: "⚠️ You have 3 no-shows - CAUTION"
├─ Priority: HIGH ⚠️
├─ Action: Consider reducing priority
└─ User Can Book (but flagged)

5th+ No-Shows:
├─ Notification: "🚫 You have 5+ no-shows!"
├─ Priority: URGENT 🚨
├─ Action: Admin review recommended
│         - Restrict booking privileges
│         - Require manual approval
│         - Possible account suspension
└─ Admin Alert Generated
```

---

## 8. System Monitoring Dashboard

```
PARKING ADMIN DASHBOARD:

Real-time Metrics:
┌────────────────────────────────────────┐
│ Total Active Assignments: 247          │
├─ Confirmed: 210 (85%)                 │
├─ Unconfirmed: 37 (15%)                │
│                                        │
│ Slots Status:                          │
├─ Available: 156                        │
├─ Assigned: 210                        │
├─ Maintenance: 12                      │
│                                        │
│ No-Show Statistics:                    │
├─ Last 24h: 8 no-shows                │
├─ This Week: 34 no-shows               │
├─ Users with 3+ no-shows: 12           │
│                                        │
│ System Health:                         │
├─ Last auto-release: 2 mins ago ✓      │
├─ Pending notifications: 5              │
├─ Database: Healthy ✓                  │
└────────────────────────────────────────┘

Recent Actions:
┌────────────────────────────────────────┐
│ [19:35] john_doe confirmed arrival    │
│ [19:30] slot_a45 auto-released        │
│ [19:25] maria_garcia confirmed        │
│ [19:20] system run auto_release (3)   │
│ [19:15] alert: user_123 5th no-show   │
└────────────────────────────────────────┘
```

---

## 9. Error Handling Scenarios

```
SCENARIO 1: User Tries to Confirm But Deadline Passed
┌──────────────────────────────────────┐
│ confirm_arrival() called              │
│ Check: now() > deadline?              │
│ YES → Deadline expired               │
│                                       │
│ Actions:                              │
│ 1. Release slot (available)          │
│ 2. Mark: status = 'no_show'         │
│ 3. Create: NoShowTracking record     │
│ 4. Send: High-priority notification  │
│                                       │
│ Response: 400 Bad Request            │
│ "Confirmation deadline has passed"   │
└──────────────────────────────────────┘

SCENARIO 2: User Tries to Confirm Twice
┌──────────────────────────────────────┐
│ confirm_arrival() called              │
│ Check: is_confirmed == True?         │
│ YES → Already confirmed              │
│                                       │
│ Response: 400 Bad Request            │
│ "Arrival already confirmed"          │
└──────────────────────────────────────┘

SCENARIO 3: User Tries to Complete Already Completed
┌──────────────────────────────────────┐
│ complete_assignment() called          │
│ Check: status == 'active'?           │
│ NO → Already completed/no-show       │
│                                       │
│ Response: 400 Bad Request            │
│ "Assignment already <status>"        │
└──────────────────────────────────────┘
```

---

## 10. Production Deployment

```
SERVER SETUP:

1. Cron Job (every 1 minute):
   * * * * * /usr/bin/python /app/manage.py auto_release_unconfirmed

2. Or Celery Beat (recommended):
   CELERY_BEAT_SCHEDULE = {
       'auto_release': {
           'task': 'parking_app.tasks.auto_release',
           'schedule': crontab(minute='*/1')
       }
   }

3. Database Optimization:
   - Index on (is_confirmed, confirmation_deadline)
   - Index on (user_id, created_at) in NoShowTracking
   - Regular backups

4. Monitoring:
   - Alert if auto_release hasn't run in 5 mins
   - Alert if no-show tracking falls behind
   - Daily summary report

5. Notifications:
   - Push notifications to mobile app
   - Email notifications
   - In-app notifications
   - SMS for critical alerts
```

All diagrams are ready for your presentation! 📊
