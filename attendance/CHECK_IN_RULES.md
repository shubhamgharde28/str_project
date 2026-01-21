# Attendance Check-In Rules

## Overview
The attendance system has been updated with proper check-in timing rules to enforce punctuality.

## Rules

### Standard Check-In Time: 10:30 AM (Indian Standard Time)

1. **On-Time Check-In**: If employee checks in by **10:45:00 AM**
   - `is_half_day = False`
   - Full day attendance recorded
   - Status: ✅ On Time

2. **Late Check-In**: If employee checks in after **10:45:00 AM**
   - `is_half_day = True`
   - Half-day attendance recorded
   - Status: ⚠️ Late (Half Day)
   - Grace Period: 15 minutes (10:30 AM to 10:45 AM)

## API Response Example

### Successful On-Time Check-In
```json
{
  "message": "Successfully checked in.",
  "check_in_time": "10:30 AM",
  "is_half_day": false,
  "attendance": { ... }
}
```

### Late Check-In (Half-Day)
```json
{
  "message": "Successfully checked in. (Half day marked - check-in after 10:45 AM)",
  "check_in_time": "10:46 AM",
  "is_half_day": true,
  "attendance": { ... }
}
```

## Database Field
- **Field**: `is_half_day` (BooleanField)
- **Model**: `Attendance`
- **Default**: `False`
- **Description**: Marks whether an attendance record is a half-day due to late check-in

## Implementation Details
- Check-in validation happens in `AttendanceCheckInView`
- Time comparison uses local Indian timezone
- Automatic calculation: if `check_in_time > 10:45:00 AM`, then `is_half_day = True`
- The `AttendanceSerializer` now includes `is_half_day` field in all API responses

## Testing the Endpoint

### Check-In API
- **Endpoint**: `POST /api/attendance/check-in/`
- **Auth**: JWT Token (Bearer)
- **Payload**:
  ```json
  {
    "latitude": "28.6139",
    "longitude": "77.2090"
  }
  ```
- **Response Includes**:
  - `check_in_time`: Time of check-in
  - `is_half_day`: Boolean indicating half-day status
  - Full attendance object with all fields

## Future Enhancements
- Add email/SMS notification when half-day is marked
- Add admin override capability for exceptional cases
- Add reporting to show half-day attendance trends
- Integrate with salary calculation system
