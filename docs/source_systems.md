# Source Systems

| Domain | Table | Type | Grain | Primary Key |
|---|---|---|---|---|
| HR | hr.employees | Master | 1 row = 1 employee | employee_id |
| HR | hr.departments | Reference | 1 row = 1 department | department_id |
| HR | hr.positions | Reference | 1 row = 1 position | position_id |
| Office | office.offices | Reference | 1 row = 1 office | office_id |
| Access | access.doors | Master | 1 row = 1 door | door_id |
| Access | access.access_events | Event | 1 row = 1 access event | event_id |
| Meeting | meeting.rooms | Master | 1 row = 1 room | room_id |
| Meeting | meeting.bookings | Transaction | 1 row = 1 booking | booking_id |
| Signing | signing.documents | Transaction | 1 row = 1 document | document_id |
| Signing | signing.signing_requests | Transaction | 1 row = 1 signing request | request_id |
| IoT | iot.devices | Master | 1 row = 1 device | device_id |
| IoT | iot.device_events | Event | 1 row = 1 device event | event_id |

## hr.employees
Grain: 1 row = 1 employee

Columns:
- employee_id BIGINT PK
- employee_code VARCHAR
- full_name VARCHAR
- email VARCHAR
- phone VARCHAR
- department_id BIGINT
- position_id BIGINT
- office_id BIGINT
- manager_id BIGINT
- hire_date DATE
- termination_date DATE
- employment_type VARCHAR
- status VARCHAR
- created_at TIMESTAMP
- updated_at TIMESTAMP

Business Key: employee_code
CDC behavior: INSERT / UPDATE / DELETE
PII: full_name, email, phone, employee_code

## hr.departments
Grain: 1 row = 1 department

Columns:
- department_id BIGINT PK
- department_code VARCHAR
- department_name VARCHAR
- manager_id BIGINT
- created_at TIMESTAMP
- updated_at TIMESTAMP

Business Key: department_code
CDC behavior: INSERT / UPDATE / DELETE
PII: None

## hr.positions
Grain: 1 row = 1 position

Columns:
- position_id BIGINT PK
- position_code VARCHAR
- title VARCHAR
- level VARCHAR
- created_at TIMESTAMP
- updated_at TIMESTAMP

Business Key: position_code
CDC behavior: INSERT / UPDATE / DELETE
PII: None

## office.offices
Grain: 1 row = 1 office

Columns:
- office_id BIGINT PK
- office_code VARCHAR
- office_name VARCHAR
- location VARCHAR
- capacity INT
- created_at TIMESTAMP
- updated_at TIMESTAMP

Business Key: office_code
CDC behavior: INSERT / UPDATE / DELETE
PII: None

## access.doors
Grain: 1 row = 1 door

Columns:
- door_id BIGINT PK
- door_code VARCHAR
- door_name VARCHAR
- office_id BIGINT
- status VARCHAR
- created_at TIMESTAMP
- updated_at TIMESTAMP

Business Key: door_code
CDC behavior: INSERT / UPDATE / DELETE
PII: None

## access.access_events
Grain: 1 row = 1 access event

Columns:
- event_id BIGINT PK
- door_id BIGINT
- employee_id BIGINT
- event_time TIMESTAMP
- access_type VARCHAR (IN/OUT)
- status VARCHAR (SUCCESS/DENIED)
- created_at TIMESTAMP

Business Key: event_id
CDC behavior: APPEND-ONLY (Mutable: NO)
PII: None

## meeting.rooms
Grain: 1 row = 1 room

Columns:
- room_id BIGINT PK
- room_code VARCHAR
- room_name VARCHAR
- office_id BIGINT
- capacity INT
- amenities VARCHAR
- status VARCHAR
- created_at TIMESTAMP
- updated_at TIMESTAMP

Business Key: room_code
CDC behavior: INSERT / UPDATE / DELETE
PII: None

## meeting.bookings
Grain: 1 row = 1 booking

Columns:
- booking_id BIGINT PK
- room_id BIGINT
- organizer_id BIGINT (Employee)
- title VARCHAR
- start_time TIMESTAMP
- end_time TIMESTAMP
- status VARCHAR (PENDING -> CONFIRMED -> CANCELLED/COMPLETED)
- created_at TIMESTAMP
- updated_at TIMESTAMP

Business Key: booking_id
CDC behavior: INSERT / UPDATE
PII: None

## signing.documents
Grain: 1 row = 1 document

Columns:
- document_id BIGINT PK
- document_code VARCHAR
- title VARCHAR
- document_type VARCHAR
- creator_id BIGINT (Employee)
- status VARCHAR (DRAFT -> PENDING -> COMPLETED/REJECTED)
- created_at TIMESTAMP
- updated_at TIMESTAMP

Business Key: document_code
CDC behavior: INSERT / UPDATE / DELETE
PII: None

## signing.signing_requests
Grain: 1 row = 1 signing request

Columns:
- request_id BIGINT PK
- document_id BIGINT
- signer_id BIGINT (Employee)
- status VARCHAR (PENDING -> SIGNED/REJECTED)
- signed_at TIMESTAMP
- created_at TIMESTAMP
- updated_at TIMESTAMP

Business Key: request_id
CDC behavior: INSERT / UPDATE
PII: None

## iot.devices
Grain: 1 row = 1 device

Columns:
- device_id BIGINT PK
- device_code VARCHAR
- device_type VARCHAR
- office_id BIGINT
- room_id BIGINT (nullable)
- status VARCHAR (ACTIVE/INACTIVE/MAINTENANCE)
- created_at TIMESTAMP
- updated_at TIMESTAMP

Business Key: device_code
CDC behavior: INSERT / UPDATE / DELETE
PII: None

## iot.device_events
Grain: 1 row = 1 device event

Columns:
- event_id BIGINT PK
- device_id BIGINT
- event_time TIMESTAMP
- event_type VARCHAR (TEMPERATURE/HUMIDITY/MOTION)
- metric_value DECIMAL
- created_at TIMESTAMP

Business Key: event_id
CDC behavior: APPEND-ONLY (High volume)
PII: None