-- ==========================================
-- 1. CREATE SCHEMAS
-- ==========================================
CREATE SCHEMA IF NOT EXISTS hr;
CREATE SCHEMA IF NOT EXISTS office;
CREATE SCHEMA IF NOT EXISTS access;
CREATE SCHEMA IF NOT EXISTS meeting;
CREATE SCHEMA IF NOT EXISTS signing;
CREATE SCHEMA IF NOT EXISTS iot;

-- ==========================================
-- 2. CREATE TABLES (HR & Office)
-- ==========================================

-- Departments table is created first because Employees depends on it.
-- manager_id is initially NULL to avoid circular dependency.
CREATE TABLE hr.departments (
    department_id BIGSERIAL PRIMARY KEY,
    department_code VARCHAR(50) UNIQUE NOT NULL,
    department_name VARCHAR(255) NOT NULL,
    manager_id BIGINT, 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE hr.positions (
    position_id BIGSERIAL PRIMARY KEY,
    position_code VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    level VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE office.offices (
    office_id BIGSERIAL PRIMARY KEY,
    office_code VARCHAR(50) UNIQUE NOT NULL,
    office_name VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    address TEXT NOT NULL,
    timezone VARCHAR(50) NOT NULL DEFAULT 'Asia/Ho_Chi_Minh',
    capacity INT CHECK (capacity > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE hr.employees (
    employee_id BIGSERIAL PRIMARY KEY,
    employee_code VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    department_id BIGINT REFERENCES hr.departments(department_id),
    position_id BIGINT REFERENCES hr.positions(position_id),
    office_id BIGINT REFERENCES office.offices(office_id),
    manager_id BIGINT REFERENCES hr.employees(employee_id),
    hire_date DATE NOT NULL,
    termination_date DATE,
    employment_type VARCHAR(50),
    status VARCHAR(50) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add manager_id FK for departments after the employees table is created
ALTER TABLE hr.departments 
    ADD CONSTRAINT fk_department_manager 
    FOREIGN KEY (manager_id) REFERENCES hr.employees(employee_id);


-- ==========================================
-- 3. CREATE TABLES (Access)
-- ==========================================
CREATE TABLE access.doors (
    door_id BIGSERIAL PRIMARY KEY,
    door_code VARCHAR(50) UNIQUE NOT NULL,
    door_name VARCHAR(255) NOT NULL,
    office_id BIGINT REFERENCES office.offices(office_id),
    status VARCHAR(50) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE access.access_events (
    event_id BIGSERIAL PRIMARY KEY,
    door_id BIGINT REFERENCES access.doors(door_id),
    employee_id BIGINT REFERENCES hr.employees(employee_id),
    event_time TIMESTAMP NOT NULL,
    access_type VARCHAR(50) CHECK (access_type IN ('IN', 'OUT')),
    status VARCHAR(50) CHECK (status IN ('SUCCESS', 'DENIED')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ==========================================
-- 4. CREATE TABLES (Meeting)
-- ==========================================
CREATE TABLE meeting.rooms (
    room_id BIGSERIAL PRIMARY KEY,
    room_code VARCHAR(50) UNIQUE NOT NULL,
    room_name VARCHAR(255) NOT NULL,
    office_id BIGINT REFERENCES office.offices(office_id),
    floor INT,
    capacity INT CHECK (capacity > 0),
    has_projector BOOLEAN DEFAULT FALSE,
    has_video_conference BOOLEAN DEFAULT FALSE,
    has_whiteboard BOOLEAN DEFAULT FALSE,
    status VARCHAR(50) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE meeting.bookings (
    booking_id BIGSERIAL PRIMARY KEY,
    room_id BIGINT REFERENCES meeting.rooms(room_id),
    organizer_id BIGINT REFERENCES hr.employees(employee_id),
    title VARCHAR(255) NOT NULL, -- Potentially Sensitive
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    attendee_count INT CHECK (attendee_count > 0),
    status VARCHAR(50) CHECK (status IN ('PENDING', 'CONFIRMED', 'COMPLETED', 'CANCELLED', 'NO_SHOW')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_time_range CHECK (end_time > start_time)
);


-- ==========================================
-- 5. CREATE TABLES (Signing)
-- ==========================================
CREATE TABLE signing.documents (
    document_id BIGSERIAL PRIMARY KEY,
    document_code VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL, -- Potentially Sensitive
    document_type VARCHAR(100),
    creator_id BIGINT REFERENCES hr.employees(employee_id),
    status VARCHAR(50) CHECK (status IN ('DRAFT', 'PENDING_SIGNATURE', 'COMPLETED', 'REJECTED', 'CANCELLED')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE signing.signing_requests (
    request_id BIGSERIAL PRIMARY KEY,
    document_id BIGINT REFERENCES signing.documents(document_id),
    requester_id BIGINT REFERENCES hr.employees(employee_id),
    signer_id BIGINT REFERENCES hr.employees(employee_id),
    signing_order INT CHECK (signing_order > 0),
    status VARCHAR(50) CHECK (status IN ('PENDING', 'SIGNED', 'REJECTED')),
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    signed_at TIMESTAMP,
    rejected_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ==========================================
-- 6. CREATE TABLES (IoT)
-- ==========================================
CREATE TABLE iot.devices (
    device_id BIGSERIAL PRIMARY KEY,
    device_code VARCHAR(50) UNIQUE NOT NULL,
    device_type VARCHAR(100) NOT NULL,
    office_id BIGINT REFERENCES office.offices(office_id),
    room_id BIGINT REFERENCES meeting.rooms(room_id),
    status VARCHAR(50) CHECK (status IN ('ACTIVE', 'INACTIVE', 'MAINTENANCE')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE iot.device_events (
    event_id BIGSERIAL PRIMARY KEY,
    device_id BIGINT REFERENCES iot.devices(device_id),
    event_time TIMESTAMP NOT NULL,
    metric_type VARCHAR(50) CHECK (metric_type IN ('TEMPERATURE', 'HUMIDITY', 'CO2', 'OCCUPANCY')),
    metric_value DECIMAL(10, 2) NOT NULL,
    unit VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
