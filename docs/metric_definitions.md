# Metric Definitions

| Metric | Definition | Numerator | Denominator | Grain | Refresh |
|---|---|---|---|---|---|
| `daily_office_attendance` | Unique employees with successful IN | distinct attended employees | — | date + office | 15 min |
| `department_attendance_rate` | Attended / active employees | attended employees | active employees | date + department | daily |
| `office_entry_count` | Total IN events | total IN events | — | date + office + hour | hourly |
| `meeting_room_utilization_rate` | Used / available minutes | used minutes | available minutes | date + room | hourly |
| `booking_cancellation_rate` | Cancelled / eligible bookings | cancelled bookings | non-pending bookings | month + office | daily |
| `booking_no_show_rate` | No-show / (Completed + No-show) | no-show bookings | completed + no-show bookings | month + office | daily |
| `avg_signer_turnaround_hours` | Signed_at - Requested_at | total turnaround duration | request count | request | hourly |
| `avg_document_completion_hours` | Completed_at - Created_at | total document duration | document count | document | hourly |
