# Business Requirements

## BR-001 — Daily Office Attendance

### Business Question
How many unique employees attend each office every day?

### Consumer
- HR
- Management
- Office Operations

### Business Definition
An employee is considered to have attended the office if they have at least one access event with `access_type = IN` and `status = SUCCESS` on that day at that office.

### Grain
1 row = 1 date + 1 office

### Metrics
- `daily_unique_employees`
- `total_entry_events`

### Dimensions
- Date
- Office
- Department

### Source Tables
- `access.access_events`
- `access.doors`
- `office.offices`
- `hr.employees`

### Exclusions
- `DENIED` events
- `OUT` events
- Inactive/test employees

### Freshness
Near real-time / < 15 minutes

### Candidate Gold Model
`mart_office_daily`

---

## BR-002 — Department Attendance Rate

### Business Question
Which departments have the highest attendance rate?

### Consumer
- HR
- Management

### Business Definition
The ratio of unique attended employees to the total number of active employees in a department on a given day.

### Grain
1 row = 1 date + 1 office + 1 department

### Metrics
- `department_attendance_count`
- `department_attendance_rate`

### Dimensions
- Date
- Office
- Department

### Source Tables
- `access.access_events`
- `access.doors`
- `office.offices`
- `hr.employees`
- `hr.departments`

### Exclusions
- `DENIED` events
- `OUT` events
- Inactive/test employees

### Freshness
Daily

### Candidate Gold Model
`mart_department_attendance`

---

## BR-003 — Peak Office Entry Hour

### Business Question
What is the peak hour for employee entries into the office?

### Consumer
- Security
- Office Operations
- Management

### Business Definition
The hour of the day with the highest count of successful `IN` access events, calculated using the local office timezone.

### Grain
1 row = 1 date + 1 office + 1 hour

### Metrics
- `office_entry_count`
- `peak_entry_hour`

### Dimensions
- Date
- Office
- Hour

### Source Tables
- `access.access_events`
- `access.doors`
- `office.offices`

### Exclusions
- `DENIED` events
- `OUT` events
- Inactive/test employees

### Freshness
Hourly

### Candidate Gold Model
`mart_office_hourly_traffic`

---

## BR-004 — Meeting Room Utilization

### Business Question
How well are meeting rooms being utilized?

### Consumer
- Office Operations
- Management

### Business Definition
The percentage of available room time that is actively used for meetings. Calculated as `used_minutes` / `available_minutes`. Only `COMPLETED` meetings are counted as actual utilization.

### Grain
1 row = 1 date + 1 room

### Metrics
- `meeting_room_utilization_rate`
- `used_minutes`
- `available_minutes`

### Dimensions
- Date
- Office
- Room

### Source Tables
- `meeting.bookings`
- `meeting.rooms`
- `office.offices`

### Exclusions
- `CANCELLED` bookings
- `NO_SHOW` bookings (excluded from actual utilization)
- Inactive rooms

### Freshness
Hourly

### Candidate Gold Model
`mart_meeting_room_utilization`

---

## BR-005 — Booking Cancellation and No-show Rate

### Business Question
What is the rate of cancelled meetings and no-shows?

### Consumer
- Office Operations

### Business Definition
- Cancellation Rate = Cancelled Bookings / Eligible non-pending Bookings.
- No-show Rate = No-show Bookings / (Completed + No-show Bookings).

### Grain
1 row = 1 month (or date) + 1 office

### Metrics
- `booking_cancellation_rate`
- `booking_no_show_rate`

### Dimensions
- Date
- Office
- Room
- Organizer Department

### Source Tables
- `meeting.bookings`
- `meeting.rooms`
- `hr.employees`

### Exclusions
- `PENDING` bookings

### Freshness
Daily

### Candidate Gold Model
`mart_meeting_efficiency`

---

## BR-006 — Signing Turnaround Time

### Business Question
How long does it take to process digital signatures?

### Consumer
- Administration
- Legal
- Management

### Business Definition
- Signer Turnaround: Time taken from request to sign (`signed_at` - `requested_at`).
- Document Completion: Time taken from document creation to full completion.

### Grain
1 row = 1 request (for signer TAT) / 1 document (for document TAT)

### Metrics
- `avg_signer_turnaround_hours`
- `avg_document_completion_hours`

### Dimensions
- Date
- Department
- Document Type
- Signer

### Source Tables
- `signing.documents`
- `signing.signing_requests`
- `hr.employees`
- `hr.departments`

### Exclusions
- `CANCELLED` documents
- `REJECTED` documents (if not considered in completion TAT)

### Freshness
Hourly

### Candidate Gold Model
`mart_signing_performance`
