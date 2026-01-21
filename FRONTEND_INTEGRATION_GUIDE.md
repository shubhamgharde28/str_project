# 🚀 Frontend Integration Guide - All API Changes

**Date**: January 20, 2026  
**Summary**: Complete guide for frontend developers on all updated/new APIs

---

## 📋 Table of Contents

1. [Attendance APIs](#attendance-apis)
2. [Notifications APIs](#notifications-apis)
3. [Data Models & Response Examples](#data-models--response-examples)
4. [Frontend Implementation Examples](#frontend-implementation-examples)

---

## 🕐 Attendance APIs

### 1. **Check-In API** ⭐ UPDATED
**Endpoint**: `POST /api/attendance/check-in/`  
**Auth Required**: Yes (JWT Token)

#### What Changed:
- ✅ Added `is_half_day` field (boolean)
- ✅ Added `status` field (present/half_day/absent)
- ✅ Added `status_display` field with emoji

#### Request Body:
```json
{
  "latitude": "28.6139",
  "longitude": "77.2090"
}
```

#### Response (On-Time):
```json
{
  "message": "Successfully checked in.",
  "check_in_time": "10:30 AM",
  "is_half_day": false,
  "status": "present",
  "status_display": "✅ Present",
  "attendance": {
    "id": 1,
    "user": 2,
    "date": "2026-01-20",
    "check_in_time": "2026-01-20T10:30:00+05:30",
    "check_out_time": null,
    "is_half_day": false,
    "status": "present",
    "status_display": "✅ Present"
  }
}
```

#### Response (Late - Half-Day):
```json
{
  "message": "Successfully checked in. (Half day marked - check-in after 10:45 AM)",
  "check_in_time": "10:46 AM",
  "is_half_day": true,
  "status": "half_day",
  "status_display": "⚠️ Half Day",
  "attendance": {
    "id": 1,
    "user": 2,
    "date": "2026-01-20",
    "check_in_time": "2026-01-20T10:46:00+05:30",
    "is_half_day": true,
    "status": "half_day",
    "status_display": "⚠️ Half Day"
  }
}
```

#### Frontend Changes Needed:
```javascript
// Store the status for display
const handleCheckIn = async (latitude, longitude) => {
  try {
    const response = await fetch('/api/attendance/check-in/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ latitude, longitude })
    });
    
    const data = await response.json();
    
    // NEW: Display status with emoji
    console.log(`Status: ${data.status_display}`); // ✅ Present or ⚠️ Half Day
    console.log(`Is Half Day: ${data.is_half_day}`);
    
    // NEW: Check if half-day warning needed
    if (data.is_half_day) {
      showWarning('You have checked in late. This will be marked as half-day.');
    }
    
    // Store attendance data
    setAttendanceData(data.attendance);
  } catch (error) {
    console.error('Check-in failed:', error);
  }
};
```

---

### 2. **Check-Out API** ⭐ UPDATED
**Endpoint**: `POST /api/attendance/check-out/`

#### What Changed:
- ✅ Added `status` field in response
- ✅ Added `status_display` field in response

#### Response:
```json
{
  "message": "Successfully checked out.",
  "check_out_time": "06:30 PM",
  "status": "present",
  "status_display": "✅ Present",
  "attendance": {
    "id": 1,
    "check_in_time": "2026-01-20T10:30:00+05:30",
    "check_out_time": "2026-01-20T18:30:00+05:30",
    "status": "present",
    "status_display": "✅ Present"
  }
}
```

#### Frontend Changes:
```javascript
const handleCheckOut = async (latitude, longitude) => {
  const response = await fetch('/api/attendance/check-out/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ latitude, longitude })
  });
  
  const data = await response.json();
  
  // NEW: Display final status
  console.log(`Final Status: ${data.status_display}`);
  showSuccess(`Check-out successful. Status: ${data.status_display}`);
};
```

---

### 3. **Monthly Attendance Summary** ⭐ UPDATED
**Endpoint**: `GET /api/attendance/summary/`

#### What Changed:
- ✅ Split `total_present_days` and `total_half_days`
- ✅ Added `last_status` and `last_status_display` fields
- ✅ Added full `attendance_records` array with status for each day

#### Response:
```json
{
  "month": 1,
  "year": 2026,
  "total_days_in_month": 31,
  "total_present_days": 15,
  "total_half_days": 3,
  "total_absent_days": 13,
  "last_date": "2026-01-20",
  "last_check_in_time": "2026-01-20T10:30:00+05:30",
  "last_check_out_time": "2026-01-20T18:30:00+05:30",
  "last_status": "present",
  "last_status_display": "✅ Present",
  "attendance_records": [
    {
      "id": 1,
      "date": "2026-01-20",
      "check_in_time": "2026-01-20T10:30:00+05:30",
      "check_out_time": "2026-01-20T18:30:00+05:30",
      "is_half_day": false,
      "status": "present",
      "status_display": "✅ Present"
    },
    {
      "id": 2,
      "date": "2026-01-19",
      "check_in_time": "2026-01-19T10:46:00+05:30",
      "check_out_time": "2026-01-19T18:00:00+05:30",
      "is_half_day": true,
      "status": "half_day",
      "status_display": "⚠️ Half Day"
    },
    {
      "id": 3,
      "date": "2026-01-18",
      "check_in_time": null,
      "check_out_time": null,
      "is_half_day": false,
      "status": "absent",
      "status_display": "❌ Absent"
    }
  ]
}
```

#### Frontend Changes:
```javascript
const fetchAttendanceSummary = async () => {
  const response = await fetch('/api/attendance/summary/', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  const data = await response.json();
  
  // NEW: Display breakdown by status
  console.log(`Present: ${data.total_present_days} days`);
  console.log(`Half-Day: ${data.total_half_days} days`);
  console.log(`Absent: ${data.total_absent_days} days`);
  
  // NEW: Show calendar with status colors
  data.attendance_records.forEach(record => {
    // Green for present, Yellow for half-day, Red for absent
    const color = {
      'present': '#4CAF50',
      'half_day': '#FFC107',
      'absent': '#F44336'
    }[record.status];
    
    displayCalendarDay(record.date, record.status_display, color);
  });
};
```

---

### 4. **Admin Attendance Summary** ✨ NEW
**Endpoint**: `GET /api/attendance/admin-summary/`  
**Auth**: Superuser Only

#### Query Parameters:
- `month=1` - Month (default: current)
- `year=2026` - Year (default: current)
- `user_id=5` - Filter by specific user
- `date=2026-01-20` - Filter by date
- `status=present|half_day|absent` - Filter by status

#### Example Requests:
```
GET /api/attendance/admin-summary/?month=1&year=2026
GET /api/attendance/admin-summary/?status=half_day
GET /api/attendance/admin-summary/?user_id=5&month=1
```

#### Response:
```json
{
  "month": 1,
  "year": 2026,
  "filters_applied": {
    "date": null,
    "user_id": null,
    "status": null
  },
  "summary": {
    "total_records": 450,
    "present": 380,
    "half_day": 45,
    "absent": 25
  },
  "users_statistics": {
    "user1@gmail.com": {
      "user_id": 1,
      "email": "user1@gmail.com",
      "present": 20,
      "half_day": 2,
      "absent": 8
    },
    "user2@gmail.com": {
      "user_id": 2,
      "email": "user2@gmail.com",
      "present": 18,
      "half_day": 3,
      "absent": 9
    }
  },
  "attendance_records": [...]
}
```

#### Frontend Changes (Admin Dashboard):
```javascript
const fetchAdminAttendance = async (filters = {}) => {
  const params = new URLSearchParams();
  if (filters.month) params.append('month', filters.month);
  if (filters.year) params.append('year', filters.year);
  if (filters.status) params.append('status', filters.status);
  if (filters.user_id) params.append('user_id', filters.user_id);
  
  const response = await fetch(
    `/api/attendance/admin-summary/?${params}`,
    { headers: { 'Authorization': `Bearer ${token}` } }
  );
  
  const data = await response.json();
  
  // Display summary cards
  displaySummaryCards({
    present: data.summary.present,
    halfDay: data.summary.half_day,
    absent: data.summary.absent
  });
  
  // Display user statistics table
  displayUserStatistics(data.users_statistics);
  
  // Display attendance records with status
  displayAttendanceTable(data.attendance_records);
};
```

---

## 🔔 Notifications APIs

### 5. **List Notifications** ✨ NEW
**Endpoint**: `GET /api/notifications/`

#### Query Parameters:
- `notify_date=2026-01-20` - Filter by date
- `is_read=true|false` - Filter by read status
- `user=5` - (Superuser only) Filter by user

#### Response:
```json
[
  {
    "id": 1,
    "message": "You have workplan today: Site Visit, Presentation",
    "notify_date": "2026-01-20",
    "is_read": false,
    "created_at": "2026-01-20T09:00:00Z",
    "metadata": {
      "workplan_id": 3
    }
  },
  {
    "id": 2,
    "message": "You have a follow-up today: Customer meeting completed",
    "notify_date": "2026-01-20",
    "is_read": false,
    "created_at": "2026-01-20T08:30:00Z",
    "metadata": {
      "daily_summary_id": 5
    }
  }
]
```

#### Frontend Changes:
```javascript
const fetchNotifications = async () => {
  const response = await fetch('/api/notifications/?is_read=false', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  const notifications = await response.json();
  
  // Display notification badge with count
  displayNotificationBadge(notifications.length);
  
  // Display notifications in dropdown/list
  notifications.forEach(notif => {
    const icon = notif.metadata.workplan_id ? '📋' : '📞';
    displayNotification(notif, icon);
  });
};
```

---

### 6. **Get Unread Count** ✨ NEW
**Endpoint**: `GET /api/notifications/unread_count/`

#### Response:
```json
{
  "unread_count": 3
}
```

#### Frontend Changes:
```javascript
const updateNotificationBadge = async () => {
  const response = await fetch('/api/notifications/unread_count/', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  const data = await response.json();
  
  // Update badge number
  document.querySelector('.notification-badge').textContent = data.unread_count;
  
  // Show dot if unread count > 0
  if (data.unread_count > 0) {
    document.querySelector('.notification-dot').style.display = 'block';
  }
};

// Refresh every 30 seconds
setInterval(updateNotificationBadge, 30000);
```

---

### 7. **Mark Notification Read** ✨ NEW
**Endpoint**: `POST /api/notifications/{id}/mark_read/`

#### Frontend Changes:
```javascript
const markAsRead = async (notificationId) => {
  await fetch(`/api/notifications/${notificationId}/mark_read/`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  // Update UI
  document.querySelector(`[data-id="${notificationId}"]`).classList.add('read');
  updateNotificationBadge();
};
```

---

### 8. **Mark All Read** ✨ NEW
**Endpoint**: `POST /api/notifications/mark_all_read/`

#### Response:
```json
{
  "marked": 5
}
```

#### Frontend Changes:
```javascript
const markAllAsRead = async () => {
  const response = await fetch('/api/notifications/mark_all_read/', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  const data = await response.json();
  console.log(`Marked ${data.marked} notifications as read`);
  
  // Clear all notification badges
  document.querySelectorAll('.notification-item').forEach(el => {
    el.classList.add('read');
  });
  updateNotificationBadge();
};
```

---

### 9. **Get User Notifications** ✨ NEW
**Endpoint**: `GET /api/notifications/user/{user_id}/`

#### Response:
```json
[
  {
    "id": 1,
    "message": "You have workplan today",
    "notify_date": "2026-01-20",
    "is_read": false,
    "created_at": "2026-01-20T09:00:00Z"
  },
  ...
]
```

#### Frontend Changes (Admin):
```javascript
const viewUserNotifications = async (userId) => {
  const response = await fetch(`/api/notifications/user/${userId}/`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  const notifications = await response.json();
  displayUserNotificationHistory(notifications);
};
```

---

## 📊 Data Models & Response Examples

### Attendance Object
```typescript
interface Attendance {
  id: number;
  user: number;
  first_name: string;
  last_name: string;
  designation: string;
  department: string;
  date: string;              // YYYY-MM-DD
  check_in_time: string;     // ISO 8601 or null
  check_in_latitude: number;
  check_in_longitude: number;
  check_out_time: string;    // ISO 8601 or null
  check_out_latitude: number;
  check_out_longitude: number;
  is_half_day: boolean;      // NEW
  status: string;            // NEW: 'present' | 'half_day' | 'absent'
  status_display: string;    // NEW: '✅ Present' | '⚠️ Half Day' | '❌ Absent'
}
```

### Notification Object
```typescript
interface Notification {
  id: number;
  message: string;
  notify_date: string;       // YYYY-MM-DD
  is_read: boolean;
  created_at: string;        // ISO 8601
  metadata: {
    workplan_id?: number;
    daily_summary_id?: number;
  };
}
```

---

## 💻 Frontend Implementation Examples

### React Component Example - Check-In/Out
```jsx
import React, { useState } from 'react';

function AttendanceCard({ token }) {
  const [status, setStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleCheckIn = async () => {
    setIsLoading(true);
    try {
      // Get user location
      const position = await new Promise((resolve, reject) => {
        navigator.geolocation.getCurrentPosition(resolve, reject);
      });

      const response = await fetch('/api/attendance/check-in/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude
        })
      });

      const data = await response.json();
      
      // NEW: Show status with emoji
      setStatus({
        message: data.message,
        statusDisplay: data.status_display,
        isHalfDay: data.is_half_day,
        time: data.check_in_time
      });

    } catch (error) {
      console.error('Check-in failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="attendance-card">
      <button 
        onClick={handleCheckIn} 
        disabled={isLoading}
        className="check-in-btn"
      >
        {isLoading ? 'Processing...' : 'Check In'}
      </button>

      {status && (
        <div className={`status-message ${status.isHalfDay ? 'warning' : 'success'}`}>
          <p>{status.statusDisplay}</p>
          <p>{status.time}</p>
          {status.isHalfDay && (
            <p className="warning-text">⚠️ Late check-in - Marked as Half Day</p>
          )}
        </div>
      )}
    </div>
  );
}

export default AttendanceCard;
```

---

### React Component Example - Notifications
```jsx
import React, { useState, useEffect } from 'react';

function NotificationPanel({ token }) {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    fetchNotifications();
    // Refresh every 30 seconds
    const interval = setInterval(fetchNotifications, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchNotifications = async () => {
    try {
      const response = await fetch('/api/notifications/?is_read=false', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      setNotifications(data);

      // Update badge
      const countResponse = await fetch('/api/notifications/unread_count/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const countData = await countResponse.json();
      setUnreadCount(countData.unread_count);
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    }
  };

  const markAsRead = async (notificationId) => {
    await fetch(`/api/notifications/${notificationId}/mark_read/`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    fetchNotifications();
  };

  return (
    <div className="notification-panel">
      <div className="notification-header">
        <h3>Notifications</h3>
        <span className="badge">{unreadCount}</span>
      </div>
      
      {notifications.map(notif => (
        <div 
          key={notif.id} 
          className="notification-item"
          onClick={() => markAsRead(notif.id)}
        >
          <p className="message">{notif.message}</p>
          <p className="date">{notif.notify_date}</p>
        </div>
      ))}
    </div>
  );
}

export default NotificationPanel;
```

---

### Vue.js Example - Admin Attendance Dashboard
```vue
<template>
  <div class="admin-attendance">
    <div class="filters">
      <select v-model="filters.status" @change="fetchData">
        <option value="">All Status</option>
        <option value="present">Present</option>
        <option value="half_day">Half Day</option>
        <option value="absent">Absent</option>
      </select>
    </div>

    <div class="summary-cards">
      <div class="card present">
        <h4>Present</h4>
        <p class="count">{{ summary.present }}</p>
      </div>
      <div class="card half-day">
        <h4>Half Day</h4>
        <p class="count">{{ summary.half_day }}</p>
      </div>
      <div class="card absent">
        <h4>Absent</h4>
        <p class="count">{{ summary.absent }}</p>
      </div>
    </div>

    <table class="attendance-table">
      <thead>
        <tr>
          <th>Name</th>
          <th>Date</th>
          <th>Check In</th>
          <th>Check Out</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="record in records" :key="record.id" :class="record.status">
          <td>{{ record.first_name }} {{ record.last_name }}</td>
          <td>{{ record.date }}</td>
          <td>{{ formatTime(record.check_in_time) }}</td>
          <td>{{ formatTime(record.check_out_time) }}</td>
          <td><span class="badge">{{ record.status_display }}</span></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  data() {
    return {
      filters: { status: '' },
      summary: { present: 0, half_day: 0, absent: 0 },
      records: []
    };
  },
  mounted() {
    this.fetchData();
  },
  methods: {
    async fetchData() {
      const params = new URLSearchParams();
      if (this.filters.status) params.append('status', this.filters.status);
      
      const response = await fetch(
        `/api/attendance/admin-summary/?${params}`,
        { headers: { 'Authorization': `Bearer ${this.$store.state.token}` } }
      );
      
      const data = await response.json();
      this.summary = data.summary;
      this.records = data.attendance_records;
    },
    formatTime(timeStr) {
      return timeStr ? new Date(timeStr).toLocaleTimeString('en-IN') : '-';
    }
  }
};
</script>

<style scoped>
.summary-cards { display: flex; gap: 20px; margin: 20px 0; }
.card { padding: 20px; border-radius: 8px; text-align: center; }
.card.present { background: #4CAF50; color: white; }
.card.half-day { background: #FFC107; color: white; }
.card.absent { background: #F44336; color: white; }
</style>
```

---

## 🎯 Summary of Changes by Component

### For Employee Dashboard:
- ✅ Show `status_display` after check-in (✅ Present or ⚠️ Half Day)
- ✅ Display warning if `is_half_day: true`
- ✅ Show attendance summary with breakdown: present days, half days, absent days
- ✅ Display notification badge with count
- ✅ Show unread notifications list

### For Admin Dashboard:
- ✅ Access `/api/attendance/admin-summary/` endpoint
- ✅ Display filters: status, user, date
- ✅ Show summary cards: total present, total half-day, total absent
- ✅ Display user statistics: per-user breakdown
- ✅ Show attendance table with status column

### For Notifications:
- ✅ Fetch unread notifications count
- ✅ Display notification list with messages
- ✅ Mark individual notifications as read
- ✅ Show notification badge

---

## 🔐 Authentication Header
All requests require:
```
Authorization: Bearer {your_jwt_token}
```

Get token from: `POST /api/token/` with email and password

---

## 📱 Mobile Considerations

```javascript
// Ensure location permission before check-in
async function requestLocationPermission() {
  try {
    const permission = await navigator.permissions.query({
      name: 'geolocation'
    });
    return permission.state === 'granted';
  } catch (e) {
    return false;
  }
}

// Handle slow networks
async function checkInWithRetry(latitude, longitude, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fetch('/api/attendance/check-in/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ latitude, longitude })
      });
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
}
```

---

## ✅ Checklist for Frontend Developers

- [ ] Update Check-In component to show `status_display`
- [ ] Add warning for `is_half_day` cases
- [ ] Update Summary view to show separate present/half-day/absent counts
- [ ] Implement Notification badge and counter
- [ ] Add Notification panel with list view
- [ ] Implement Admin Attendance dashboard with filters
- [ ] Add status colors (Green/Yellow/Red) in tables
- [ ] Handle pagination for large datasets
- [ ] Add loading spinners for API calls
- [ ] Implement error handling and retry logic
- [ ] Test with different user roles (employee/superuser)
- [ ] Verify location permissions before check-in
- [ ] Add timezone handling (IST UTC+5:30)

---

**Questions?** Refer to Postman collection: `POSTMAN_API_COLLECTION.json`
