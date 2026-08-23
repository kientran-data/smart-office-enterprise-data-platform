# Smart Office Modern Enterprise Data Platform

An end-to-end Data Engineering project that simulates a modern enterprise data platform for a Smart Office environment.

The project covers the full data lifecycle:

- Operational PostgreSQL source systems
- Change Data Capture with Debezium
- Event streaming with Apache Kafka
- Stream processing with Apache Spark
- S3-compatible Data Lake storage
- Bronze / Silver / Gold data architecture
- Data Warehouse and dimensional modeling
- Data quality and observability
- Data catalog, metadata, and lineage
- BI and analytical serving

The main goal of this project is to build a realistic Data Engineering platform from source systems to analytics while practicing production-oriented concepts such as CDC, event streaming, checkpointing, schema evolution, data quality, failure recovery, and data modeling.

---

## 1. Project Overview

The simulated company operates multiple Smart Office locations and manages several operational domains:

- Human Resources
- Office Management
- Access Control
- Meeting Rooms
- Digital Signing
- IoT Devices

The operational systems continuously generate both master data and transactional/event data.

Examples include:

- Employee lifecycle changes
- Office access events
- Meeting room bookings
- Digital document signing
- IoT telemetry
- Device heartbeat events

These operational changes are captured and propagated through the data platform in near real time.

---

## 2. Architecture

```text
                         SMART OFFICE

                    Operational Applications
                             │
                             ▼
                       PostgreSQL OLTP
                             │
                             │ WAL
                             ▼
                      Debezium CDC
                             │
                             ▼
                       Apache Kafka
                             │
                             ▼
                 Spark Structured Streaming
                             │
                             ▼
                       MinIO / S3
                             │
                ┌────────────┴────────────┐
                │                         │
             Bronze                     Silver
          Raw CDC Events          Trusted Current State
                │                         │
                └────────────┬────────────┘
                             ▼
                         Gold Layer
                    Facts / Dimensions
                             │
                             ▼
                      PostgreSQL DWH
                             │
                             ▼
                            dbt
                             │
                             ▼
                     Semantic / Metrics
                             │
                             ▼
                         Power BI
```

Cross-cutting platform components include:

```text
Airflow
├── Batch orchestration
├── Backfill
├── Reconciliation
├── dbt execution
└── Data quality workflows

Great Expectations / dbt tests
├── Data quality
└── Business validation

OpenMetadata
├── Data catalog
├── Ownership
├── Metadata
├── Classification
└── Lineage

Docker Compose
└── Local self-hosted enterprise environment
```

---

## 3. Technology Stack

### Source System

* PostgreSQL
* Python
* Psycopg
* Faker

### Change Data Capture

* PostgreSQL WAL
* Logical Replication
* Debezium
* Kafka Connect

### Streaming

* Apache Kafka
* Apache Spark Structured Streaming

### Data Lake

* MinIO
* S3-compatible storage
* Parquet

### Transformation

* PySpark
* dbt
* SQL

### Data Warehouse

* PostgreSQL

### Data Quality

* dbt tests
* Great Expectations

### Metadata & Governance

* OpenMetadata

### Orchestration

* Apache Airflow

### Infrastructure

* Docker
* Docker Compose

### Analytics

* Power BI

---

# 4. Smart Office Source System

The source PostgreSQL database is organized into six business schemas.

```text
smart_office
│
├── hr
│   ├── departments
│   ├── positions
│   └── employees
│
├── office
│   └── offices
│
├── access
│   ├── doors
│   └── access_events
│
├── meeting
│   ├── rooms
│   └── bookings
│
├── signing
│   ├── documents
│   └── signing_requests
│
└── iot
    ├── devices
    └── device_events
```

Total source tables:

```text
12
```

---

# 5. Source Data Domains

## HR

### `hr.departments`

One row represents one department.

Example departments:

* Executive
* Human Resources
* Finance
* Data & Analytics
* Engineering
* Product
* Marketing
* Operations
* Legal & Compliance
* Information Technology

---

### `hr.positions`

One row represents one employee position.

Examples:

* CEO
* CTO
* Data Manager
* Data Engineer
* Data Analyst
* Engineering Manager
* Backend Engineer
* Product Manager
* Finance Analyst

---

### `hr.employees`

One row represents one employee.

Important attributes include:

```text
employee_id
employee_code
department_id
position_id
office_id
manager_id
hire_date
termination_date
employment_type
status
```

The employee hierarchy is modeled using a self-referencing relationship:

```text
employee.manager_id
        ↓
employee.employee_id
```

---

# 6. Office Domain

### `office.offices`

Represents physical office locations.

Example offices:

```text
Hanoi
Ho Chi Minh City
Da Nang
```

Each office contains timezone and capacity information.

---

# 7. Access Control

### `access.doors`

Represents physical access points.

Example door types:

```text
ENTRY
EXIT
ROOM
RESTRICTED
```

### `access.access_events`

Append-only event table.

One row represents one employee access attempt.

Example:

```text
Employee EMP000123
08:12
HN01-ENTRY-01
IN
SUCCESS
```

Possible statuses:

```text
SUCCESS
DENIED
```

This dataset supports analytics such as:

* Daily attendance
* Peak entry hours
* Office occupancy
* Denied access rate
* Outside-hours access

---

# 8. Meeting Room Domain

### `meeting.rooms`

Represents meeting rooms and room capabilities.

Attributes include:

```text
office
floor
capacity
projector
video conference
whiteboard
```

### `meeting.bookings`

Represents meeting room reservations.

Booking lifecycle:

```text
PENDING
    ↓
CONFIRMED
    ├── COMPLETED
    ├── CANCELLED
    └── NO_SHOW
```

This dataset supports:

* Meeting room utilization
* Cancellation rate
* No-show rate
* Low-utilization room detection

---

# 9. Digital Signing

### `signing.documents`

Represents enterprise documents.

Example document types:

```text
CONTRACT
PURCHASE_ORDER
INTERNAL_REQUEST
HR_DOCUMENT
POLICY
```

Document lifecycle:

```text
DRAFT
  ↓
PENDING_SIGNATURE
  ├── COMPLETED
  ├── REJECTED
  └── CANCELLED
```

### `signing.signing_requests`

Supports one or multiple signers.

Example:

```text
Document
   │
   ├── Signer 1
   ├── Signer 2
   └── Signer 3
```

This dataset supports metrics such as:

* Average signing turnaround time
* Pending signing requests
* Document completion time
* Rejection rate

---

# 10. IoT Domain

### `iot.devices`

Represents Smart Office IoT devices.

Example device types:

```text
TEMPERATURE_SENSOR
HUMIDITY_SENSOR
CO2_SENSOR
OCCUPANCY_SENSOR
MULTI_SENSOR
```

### `iot.device_events`

High-volume append-only event table.

Possible metrics:

```text
TEMPERATURE
HUMIDITY
CO2
OCCUPANCY
HEARTBEAT
```

Example:

```text
device_id: 101
event_time: 2026-08-23 10:15:00
metric_type: TEMPERATURE
metric_value: 25.4
unit: CELSIUS
```

This dataset supports:

* Environmental monitoring
* Device availability
* Device uptime
* Sensor anomaly detection
* Office occupancy analysis

---

# 11. Historical Data Generation

A Python-based synthetic data generator creates realistic historical enterprise data.

The generator does not generate purely random records.

Business rules are applied to create realistic patterns.

Examples include:

### Employee attendance

```text
Monday-Friday
→ High office attendance

Saturday-Sunday
→ Low attendance
```

### Office arrival pattern

```text
07:00  low
08:00  high
09:00  high
10:00  decreasing
```

### Meeting bookings

Bookings respect:

* Room capacity
* Office hours
* Room availability
* Booking status lifecycle
* Non-overlapping schedules

### IoT telemetry

IoT values follow reasonable ranges and change gradually rather than being independently random.

---

# 12. Live Source Simulation

The project includes a live Python generator that simulates operational activity.

Examples:

```text
ACCESS
employee=EMP000123
type=IN
status=SUCCESS

IOT
device=DEV001
temperature=25.3

BOOKING
booking created

BOOKING
PENDING → CONFIRMED

SIGNING
PENDING → SIGNED

EMPLOYEE
department changed
```

The generator produces real database operations:

```text
INSERT
UPDATE
DELETE
```

These operations are committed to PostgreSQL and recorded in the PostgreSQL WAL.

---

# 13. Change Data Capture

PostgreSQL is configured with:

```text
wal_level = logical
```

CDC architecture:

```text
PostgreSQL
     ↓
WAL
     ↓
Logical Replication
     ↓
Replication Slot
     ↓
Debezium PostgreSQL Connector
     ↓
Kafka Connect
     ↓
Kafka
```

Debezium captures:

```text
INSERT → op = c
UPDATE → op = u
DELETE → op = d
SNAPSHOT → op = r
```

Example CDC event:

```json
{
  "before": {
    "employee_id": 100,
    "department_id": 4
  },
  "after": {
    "employee_id": 100,
    "department_id": 5
  },
  "source": {
    "schema": "hr",
    "table": "employees",
    "lsn": 123456789
  },
  "op": "u"
}
```

---

# 14. PostgreSQL Logical Replication

A dedicated PostgreSQL publication defines which source tables participate in CDC.

```text
smartoffice_pub
```

A dedicated replication slot tracks Debezium's position in the PostgreSQL WAL.

```text
smartoffice_debezium_slot
```

Important operational concepts practiced in this project include:

* WAL
* LSN
* Logical decoding
* Replication slots
* Publications
* Snapshot
* CDC recovery
* WAL retention
* Connector failure recovery

---

# 15. Apache Kafka

Kafka provides the durable event-streaming layer between CDC and downstream processing.

Example CDC topics:

```text
smartoffice.hr.employees
smartoffice.hr.departments
smartoffice.hr.positions

smartoffice.office.offices

smartoffice.access.doors
smartoffice.access.access_events

smartoffice.meeting.rooms
smartoffice.meeting.bookings

smartoffice.signing.documents
smartoffice.signing.signing_requests

smartoffice.iot.devices
smartoffice.iot.device_events
```

The project demonstrates:

* Topics
* Partitions
* Offsets
* Message keys
* Consumer groups
* Consumer lag
* Replay
* Kafka retention
* Producer/consumer decoupling

Kafka ordering is guaranteed within a partition.

Stable entity keys are used where ordering for the same entity is important.

---

# 16. Why Kafka?

Kafka decouples source change capture from downstream consumers.

```text
                    ┌── Spark
                    │
Debezium → Kafka ───┼── Monitoring
                    │
                    └── Future Consumers
```

If Spark is temporarily unavailable:

```text
PostgreSQL
     ↓
Debezium
     ↓
Kafka
     ↓
Spark ❌
```

Kafka retains the events.

When Spark recovers, it can continue processing from its previous position.

---

# 17. Why Debezium?

Using an `updated_at` incremental query is sufficient for many batch pipelines, but this project requires:

* Near-real-time changes
* INSERT capture
* UPDATE capture
* DELETE capture
* Intermediate state changes
* Reliable recovery
* Change ordering

Debezium reads PostgreSQL logical replication instead of repeatedly querying operational tables.

It also handles many complex CDC concerns such as:

```text
Replication position
Snapshot coordination
LSN tracking
Schema changes
Transaction boundaries
Reconnect
Offset management
Failure recovery
```

---

# 18. Bronze Data Lake

The next layer consumes Kafka CDC events with Spark Structured Streaming.

```text
Kafka
   ↓
Spark Structured Streaming
   ↓
MinIO / S3
   ↓
Parquet
   ↓
Bronze
```

Bronze preserves the raw CDC stream instead of immediately creating current-state tables.

Example Bronze metadata:

```text
kafka_key
kafka_value

kafka_topic
kafka_partition
kafka_offset
kafka_timestamp

source_schema
source_table

ingested_at
ingest_date
```

The combination:

```text
topic
+
partition
+
offset
```

provides a unique location for a Kafka record and is retained for lineage and debugging.

---

# 19. Why Keep Raw CDC Events?

Bronze follows an immutable event-history approach.

It preserves:

```text
Snapshot
CREATE
UPDATE
DELETE
Tombstone
```

rather than immediately removing deleted records or overwriting previous versions.

This allows downstream data to be:

* Reprocessed
* Rebuilt
* Audited
* Debugged
* Replayed

CDC resolution is performed later in the Silver layer.

---

# 20. Data Lake Layout

Planned Bronze organization:

```text
smart-office-bronze/
└── cdc/
    │
    ├── source_schema=hr/
    │   ├── source_table=employees/
    │   └── source_table=departments/
    │
    ├── source_schema=access/
    │   └── source_table=access_events/
    │
    ├── source_schema=meeting/
    │   └── source_table=bookings/
    │
    ├── source_schema=signing/
    │   └── source_table=signing_requests/
    │
    └── source_schema=iot/
        └── source_table=device_events/
```

Bronze is partitioned primarily by:

```text
source_schema
source_table
ingest_date
```

---

# 21. Streaming Checkpoints

Spark Structured Streaming checkpoints are stored separately from business data.

```text
smart-office-checkpoints/
```

Checkpointing allows Spark to recover its processing state after failure.

Conceptually:

```text
Kafka

Partition 0 → offset 1500
Partition 1 → offset 2100
Partition 2 → offset 980

            ↓

       Spark Checkpoint

            ↓

         Restart

            ↓

       Resume Processing
```

---

# 22. Medallion Architecture

The platform follows a Medallion-style architecture.

## Bronze

Purpose:

```text
Raw
Immutable
Traceable
Replayable
```

Contains:

* Raw CDC payload
* Kafka metadata
* Source metadata
* Ingestion metadata

---

## Silver

Purpose:

```text
Clean
Typed
Deduplicated
CDC-resolved
Trusted
```

Silver responsibilities include:

* Parse Debezium payload
* Resolve snapshot / create / update / delete
* Handle tombstones
* Deduplicate events
* Apply schema
* Validate data types
* Handle late-arriving data
* Build current-state datasets
* Data quality validation

---

## Gold

Purpose:

```text
Business-ready
Dimensional
Metric-oriented
```

Candidate marts include:

```text
mart_office_daily
mart_department_attendance
mart_meeting_room_utilization
mart_signing_performance
mart_device_health
mart_security_events
```

Gold will contain dimensional models such as:

```text
Dimensions
Facts
Business Metrics
```

---

# 23. Example Business Metrics

The project is designed around business questions instead of simply moving data between technologies.

Examples include:

### Daily Office Attendance

```text
COUNT(DISTINCT employee_id)
```

for employees with a successful office entry.

---

### Department Attendance Rate

```text
employees_attended
--------------------
active_employees
```

---

### Peak Entry Hour

Successful `IN` events grouped by office-local hour.

---

### Meeting Room Utilization

```text
used_minutes
--------------
available_minutes
```

---

### Signing Turnaround Time

```text
signed_at - requested_at
```

---

### Device Uptime

Derived using IoT heartbeat availability over expected monitoring time.

---

### Denied Access Rate

```text
denied_access_attempts
-----------------------
total_access_attempts
```

---

# 24. Data Quality Strategy

Data quality is enforced at multiple layers.

## Source

PostgreSQL provides:

```text
PRIMARY KEY
FOREIGN KEY
UNIQUE
NOT NULL
CHECK
```

Example:

```text
booking.end_time > booking.start_time
```

---

## Silver

Additional checks will validate:

* CDC ordering
* Duplicate events
* Null business keys
* Referential integrity
* Invalid business states
* Late-arriving events
* Sensor ranges
* Cross-table consistency

---

## Gold

Business-level validation will include:

* Metric reconciliation
* Fact/dimension relationship validation
* Grain validation
* Aggregation consistency

---

# 25. Failure Scenarios

The project intentionally tests failure and recovery scenarios.

Examples:

### Debezium failure

```text
PostgreSQL ✅
Debezium   ❌
Kafka
```

PostgreSQL continues writing WAL.

The replication slot retains changes required by Debezium.

After recovery, Debezium continues from its previous replication position.

---

### Spark failure

```text
PostgreSQL
   ↓
Debezium
   ↓
Kafka ✅
   ↓
Spark ❌
```

Kafka retains events.

Spark resumes processing using its checkpoint after restart.

---

### MinIO failure

Kafka continues buffering upstream events while the Data Lake sink is unavailable.

After storage recovery, stream processing can resume from checkpointed state.

---

# 26. Project Structure

```text
.
├── docker-compose.yml
├── .env.example
├── requirements.txt
│
├── source/
│   ├── postgres/
│   │   └── init/
│   │       ├── 01_create_schemas.sql
│   │       ├── 02_create_tables.sql
│   │       └── 03_seed_reference_data.sql
│   │
│   └── generator/
│       ├── config.py
│       ├── db.py
│       │
│       ├── historical/
│       │   ├── access_events.py
│       │   ├── meeting_bookings.py
│       │   ├── signing.py
│       │   └── device_events.py
│       │
│       ├── live/
│       │   ├── clock.py
│       │   ├── access.py
│       │   ├── iot.py
│       │   ├── meeting.py
│       │   ├── signing.py
│       │   ├── employee.py
│       │   └── delete_demo.py
│       │
│       ├── generate_master_data.py
│       ├── generate_historical_data.py
│       └── live_generator.py
│
├── debezium/
│
├── spark/
│   ├── jobs/
│   └── conf/
│
├── scripts/
│
├── reports/
│
└── docs/
```

The repository structure will continue evolving as Silver, Gold, orchestration, governance, and monitoring components are implemented.

---

# 27. Local Services

Typical local endpoints:

| Service           | Endpoint         |
| ----------------- | ---------------- |
| PostgreSQL Source | `localhost:5434` |
| Kafka             | `localhost:9092` |
| Kafka Connect     | `localhost:8083` |
| MinIO API         | `localhost:9000` |
| MinIO Console     | `localhost:9001` |
| Spark Master      | `localhost:7077` |
| Spark Master UI   | `localhost:8080` |
| Spark Worker UI   | `localhost:8081` |

Internal Docker services communicate using Docker DNS names instead of `localhost`.

For example:

```text
source-postgres:5432
kafka:19092
minio:9000
spark-master:7077
```

---

# 28. Running the Platform

Validate Docker Compose:

```bash
docker compose config
```

Start infrastructure:

```bash
docker compose up -d
```

Check services:

```bash
docker compose ps
```

Follow logs:

```bash
docker compose logs -f
```

---

# 29. Running the Live Generator

Example:

```bash
python -m source.generator.live_generator
```

The live generator continuously produces operational database changes.

These changes flow through:

```text
Python Generator
      ↓
PostgreSQL
      ↓
WAL
      ↓
Debezium
      ↓
Kafka
```

Once the Spark streaming pipeline is running:

```text
Python Generator
      ↓
PostgreSQL
      ↓
Debezium
      ↓
Kafka
      ↓
Spark
      ↓
MinIO Bronze
```

---

# 30. Development Roadmap

## Completed

* [x] Business scenario design
* [x] Source system design
* [x] PostgreSQL source infrastructure
* [x] 12 source tables
* [x] PK / FK / UNIQUE / CHECK constraints
* [x] Source indexing
* [x] Historical data generation
* [x] Live operational simulation
* [x] Kafka environment
* [x] Kafka topics / partitions / consumer groups
* [x] PostgreSQL logical replication
* [x] Debezium CDC
* [x] Initial snapshot
* [x] INSERT CDC
* [x] UPDATE CDC
* [x] DELETE CDC
* [x] CDC recovery testing
* [x] Spark Structured Streaming
* [x] MinIO Data Lake
* [x] Kafka → Bronze ingestion
* [x] Streaming checkpoint recovery

### Phase 8 Execution Metrics (Actuals)
- **CDC Topics Ingested**: 12 Topics
- **Initial Snapshot & Stream Size**: ~59 MiB of raw JSON CDC payloads
- **Bronze Data Lake Output**: 47 Parquet files (partitioned by schema/table/date)
- **Throughput**: Peaked during Initial Snapshot catch-up and efficiently idled during live stream events.

## Planned

* [ ] Silver CDC processing
* [ ] CDC deduplication
* [ ] Current-state reconstruction
* [ ] Schema evolution handling
* [ ] Data quality framework
* [ ] PostgreSQL analytical warehouse
* [ ] dbt transformations
* [ ] Dimensional modeling
* [ ] Gold business marts
* [ ] Apache Airflow orchestration
* [ ] OpenMetadata catalog
* [ ] Data lineage
* [ ] Monitoring and alerting
* [ ] Power BI semantic model
* [ ] Power BI dashboards
* [ ] CI/CD

---

# 31. Key Data Engineering Concepts Practiced

This project is designed to demonstrate practical understanding of:

```text
OLTP vs OLAP

CDC
PostgreSQL WAL
Logical Replication
Replication Slots
LSN
Publications

Kafka Topics
Partitions
Offsets
Message Keys
Consumer Groups
Consumer Lag
Replay

Structured Streaming
Event Time
Processing Time
Checkpointing
Failure Recovery

Object Storage
Parquet
Data Lake
Partitioning
Small Files

Medallion Architecture
Bronze
Silver
Gold

CDC Resolution
Deduplication
Late-arriving Data
Schema Evolution

Dimensional Modeling
Facts
Dimensions
Business Grain

Data Quality
Metadata
Lineage
Governance

Orchestration
Observability
CI/CD
```

---

# 32. Design Principles

The project follows several engineering principles.

### Preserve raw data before transformation

Bronze stores raw CDC events to support replay and debugging.

### Do not assume exactly-once delivery

Downstream processing is designed to tolerate duplicate or replayed events.

### Separate event history from current state

CDC history belongs in Bronze.

Trusted current state belongs in Silver.

### Prefer idempotent processing

Pipelines should be safe to rerun whenever possible.

### Treat failures as part of the architecture

Kafka outages, connector failures, Spark restarts, and storage failures are tested intentionally.

### Business logic drives the data model

Gold models are built from business questions and metric definitions rather than simply exposing source tables.

---

# 33. Project Goal

The final objective is not simply to demonstrate individual technologies.

The goal is to build and understand the complete lifecycle:

```text
Business Event
      ↓
Operational Database
      ↓
Transaction Log
      ↓
Change Data Capture
      ↓
Event Streaming
      ↓
Stream Processing
      ↓
Data Lake
      ↓
Trusted Data
      ↓
Dimensional Model
      ↓
Business Metrics
      ↓
Analytics
      ↓
Business Decision
```

This project is built as a hands-on environment for learning and demonstrating modern Data Engineering architecture and production-oriented engineering practices.