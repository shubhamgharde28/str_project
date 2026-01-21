# API Updates Summary - STR Project

**Date**: January 20, 2026  
**Changes**: Attendance check-in logic & Notifications system

---

## 🔄 Updated APIs

### 1. **Check-In API** ⭐ UPDATED
**Endpoint**: `POST /api/attendance/check-in/`

**New Features**:
- ✅ Automatic half-day detection
- ✅ 10:30 AM deadline with 15-min grace period (until 10:45 AM)
- ✅ `is_half_day` field in response

**Request Body**:
```json
{
  "latitude": "28.6139",
  "longitude": "77.2090"
}
```

**Response (On-Time Check-In)**:
```json
{
  "message": "Successfully checked in.",
  "check_in_time": "10:30 AM",
  "is_half_day": false,
  "attendance": {
    "id": 1,
    "user": 2,
    "date": "2026-01-20",
    "check_in_time": "2026-01-20T10:30:00+05:30",
    "is_half_day": false,
    ...
  }
}
```

**Response (Late Check-In - Half-Day)**:
```json
{
  "message": "Successfully checked in. (Half day marked - check-in after 10:45 AM)",
  "check_in_time": "10:46 AM",
  "is_half_day": true,
  "attendance": {
    "id": 1,
    "user": 2,
    "date": "2026-01-20",
    "check_in_time": "2026-01-20T10:46:00+05:30",
    "is_half_day": true,
    ...
  }
}
```

**Check-In Rules**:
| Time | Status | is_half_day |
|------|--------|-----------|
| ≤ 10:45:00 AM | ✅ On Time | `false` |
| > 10:45:00 AM | ⚠️ Late | `true` |

---

### 2. **Check-Out API** (No Changes)
**Endpoint**: `POST /api/attendance/check-out/`

Request & response format remain the same.

---

### 3. **Monthly Attendance Summary API** (No Changes)
**Endpoint**: `GET /api/attendance/summary/`

Returns attendance records for the current month. Now includes `is_half_day` field in each record.

---

## 📬 Notifications APIs

### 4. **List Notifications** ✅ NEW FEATURE
**Endpoint**: `GET /api/notifications/`

**Filters**:
- `?notify_date=YYYY-MM-DD` - Filter by date
- `?is_read=true|false` - Filter by read status
- `?user=<id>` - Superuser-only, filter by user

**Example**: Get today's unread notifications
```
GET /api/notifications/?notify_date=2026-01-20&is_read=false
```

---

### 5. **Get User Notifications** ✅ NEW FEATURE
**Endpoint**: `GET /api/notifications/user/{user_id}/`

**Access**:
- Superusers: can query any user
- Regular users: can only view own notifications

---

### 6. **Get Unread Count** ✅ NEW FEATURE
**Endpoint**: `GET /api/notifications/unread_count/`

**Response**:
```json
{
  "unread_count": 3
}
```

---

### 7. **Mark Notification Read** ✅ NEW FEATURE
**Endpoint**: `POST /api/notifications/{id}/mark_read/`

---

### 8. **Mark All Notifications Read** ✅ NEW FEATURE
**Endpoint**: `POST /api/notifications/mark_all_read/`

---

### 9. **Create Notification** ✅ NEW FEATURE
**Endpoint**: `POST /api/notifications/`

**Superuser Only**:
```json
{
  "user": 2,
  "message": "Test notification",
  "notify_date": "2026-01-20"
}
```

**Regular User** (creates for self):
```json
{
  "message": "My reminder",
  "notify_date": "2026-01-20"
}
```

---

## 🔧 Configuration Variables

In Postman collection, update these variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `base_url` | `http://localhost:8000` | API base URL |
| `access_token` | `""` | JWT Bearer token (get from login) |
| `today` | `2026-01-20` | Current date (auto-set) |
| `user_id` | `2` | Target user ID for queries |

---

## 📊 Database Schema Changes

### Attendance Model
**New Field**:
- `is_half_day` (BooleanField, default=False)

**Migration**: `0005_attendance_is_half_day.py` ✅ Applied

---

## 🔔 Automatic Notifications

Notifications are created automatically when:

1. **WorkPlan Created/Updated** with `date = today`
   - Notifies: `created_by` + all `coworkers`
   - Message: "You have workplan today: {titles}"

2. **DailySummaryReport Created/Updated** with `follow_up_date = today`
   - Notifies: Report user
   - Message: "You have a follow-up today: {summary_text}"

---

## 🧪 Testing Checklist

- [ ] Login and get token
- [ ] Check-in at 10:30 AM (verify `is_half_day=false`)
- [ ] Check-in at 10:46 AM (verify `is_half_day=true`)
- [ ] Check-out
- [ ] View attendance summary
- [ ] List notifications
- [ ] View unread count
- [ ] Mark notification as read
- [ ] Create test notification (superuser)

---

## 📝 Notes

- All times are in Indian Standard Time (IST, UTC+5:30)
- `is_half_day` is automatically calculated, not editable via API
- Notifications are created by signals (automatic) or management command
- Management command: `python manage.py generate_notifications`
