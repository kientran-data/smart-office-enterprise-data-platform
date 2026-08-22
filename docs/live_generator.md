# Live Transaction Generator

## Purpose
The Live Transaction Generator is a long-running continuous Python daemon designed to mimic the natural heartbeat of a Smart Office. Instead of generating a static baseline, it actively INSERTS, UPDATES, and DELETES data across various domains. It produces PostgreSQL WAL records that serve as the foundation for the Debezium CDC pipeline.

## Simulation Clock
To ensure events can be generated rapidly regardless of the real-world time of day, the generator operates on a decoupled **Simulation Clock**. 
By default (`SIMULATION_SPEED=60`), every 1 real-world second translates to 1 simulated minute. A full 24-hour cycle of business logic takes about 24 real minutes.

## Event Types & Frequencies
Events do not fire equally. The generator follows a probability distribution (`.env`) aligned with realistic business behavior:
- **IoT Events**: Extremely high frequency (telemetry sent every few ticks).
- **Access Events**: Medium-high frequency (Gaussian distribution, peaks between 08:00 and 09:00).
- **Bookings**: Low frequency for creations, intermittent updates.
- **Signing**: Low frequency for documents, intermittent updates.
- **Employee Changes**: Very low frequency (SCD Type 2 mutations).

## State Transitions
The daemon executes realistic business lifecycles:

### Meeting Booking Lifecycle
```text
PENDING
  ↓
CONFIRMED
  ├── COMPLETED
  ├── CANCELLED
  └── NO_SHOW
```

### Digital Signing Lifecycle
```text
PENDING
 ├── SIGNED
 ├── REJECTED
```
*Note: A Document is only marked `COMPLETED` when all underlying signing requests are resolved to `SIGNED`. If any request is `REJECTED`, the entire document is `REJECTED` in a unified database transaction.*

## Business Rules Enforced
- **Room Overlaps**: Strict constraint queries prevent meetings from overlapping in the same room.
- **IoT Smooth Telemetry**: Consecutive sensor readings drift naturally rather than bouncing erratically.
- **Employee Terminations**: Employees are never hard-deleted. They receive a `TERMINATED` status via an UPDATE to preserve historical integrity.
- **No Orphan FKs**: Transactions ensure that IDs strictly map to existing master data.

## Delete CDC Demo
While standard data uses soft deletes, CDC pipelines must occasionally handle hard deletes. 
The system features a temporary door workflow (`ENABLE_DELETE_DEMO=true` or `--emit-delete-demo`) that INSERTS a temporary record, waits briefly, and then DELETES it, yielding a clear `op = c` followed by `op = d` in Kafka.

## How to Run

**1. Run Once (Testing)**
Executes a single tick and exits immediately:
```bash
python -m source.generator.live_generator --once
```

**2. Run for Duration (Testing)**
Executes for exactly X seconds and stops:
```bash
python -m source.generator.live_generator --duration 60
```

**3. Run Continuously (Background Daemon)**
Starts the continuous simulation via Docker Compose alongside PostgreSQL:
```bash
docker-compose up -d live-generator
docker-compose logs -f live-generator
```

## Known Limitations
- The generator prioritizes business consistency over perfect scientific simulation. IoT temperature variations use uniform drifting rather than complex thermodynamic physics models.
- If stopped and started days later, the simulation clock may jump depending on `.env` configuration.
