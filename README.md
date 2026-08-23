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