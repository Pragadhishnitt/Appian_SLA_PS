# Appian SLA Predictive Simulation

A process mining and predictive simulation platform for Appian workflows. Uses ML to predict activity durations, next activities, and SLA breach risks with real-time event streaming.

## 📚 Documentation

**📖 [Complete Documentation (PDF)](docs/documentation.pdf)** - 30-page comprehensive guide covering:
- System Architecture & Design
- Machine Learning Models
- API Reference
- Installation & Deployment
- Troubleshooting & Best Practices
  
## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Data Simulator │────▶│      Kafka      │────▶│   ClickHouse    │
│     :8001       │     │     :29092      │     │     :8123       │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                          │
┌─────────────────┐     ┌─────────────────┐     ┌────────▼────────┐
│   Simulation    │◀───▶│   Inference     │◀───▶│   SLA Monitor   │
│   Sandbox :8003 │     │     :8004       │     │     :8002       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                          │
                                                          ▼
                                                ┌─────────────────┐
                                                │   Demo UI       │
                                                │     :8090       │
                                                └─────────────────┘
```

## 🚀 Quick Start

```bash
# 1. Start all services
docker compose up -d --build

# 2. Check services are running
docker compose ps

# 3. Generate test data (50 cases → ~400 events)
curl -X POST http://localhost:8001/api/generate \
  -H "Content-Type: application/json" \
  -d '{"num_cases": 50}'

# 4. Wait for data to flow through Kafka → ClickHouse (5-10 seconds)
sleep 8

# 5. Verify data in ClickHouse
docker exec clickhouse clickhouse-client --query "SELECT count() FROM events"

# 6. Open the Demo UI
cd demo
python3 server.py
# Then open http://localhost:8090 in your browser
```

## 📦 Core Services

| Service | Port | Status | Description |
|---------|------|--------|-------------|
| **Data Simulator** | 8001 | ✅ Active | Generates realistic loan application events |
| **SLA Monitor** | 8002 | ✅ Active | Real-time SLA breach prediction & bottleneck detection |
| **Simulation Sandbox** | 8003 | ✅ Active | What-if scenario testing |
| **Inference** | 8004 | ✅ Active | ML model serving (XGBoost) |
| **ClickHouse** | 8123 | ✅ Active | Event storage & analytics database |
| **Kafka** | 29092 | ✅ Active | Event streaming platform |
| **Demo UI** | 8090 | ✅ Active | Interactive dashboard with ClickHouse query executor |

## 🎯 Key Features

### 1. Real-time Event Generation
- Generates realistic loan application process events
- Simulates variability (peak hours, agent availability, customer tiers)
- Configurable case volume and complexity

### 2. SLA Breach Prediction
- Forecasts which cases will breach SLA deadlines
- Provides breach probability and time to deadline
- Proactive alerting for at-risk cases

### 3. Bottleneck Detection
- Identifies process bottlenecks in real-time
- Calculates queue depths and resource utilization
- Provides actionable recommendations

### 4. What-If Simulation
- Test scenarios before implementing changes
- Compare baseline vs modified resource allocation
- Measure impact on SLA compliance and throughput

### 5. ML-Powered Predictions
- **Duration Predictor**: Estimates activity completion time
- **Routing Predictor**: Predicts next activity in process
- **SLA Breach Predictor**: Calculates breach probability

### 6. Interactive Demo UI
- Live dashboard with real-time metrics
- ClickHouse SQL query executor
- Manual prediction forms
- Scenario builder and comparison

## 🧪 Testing the Services

### 1. Data Simulator
```bash
# Generate events
curl -X POST http://localhost:8001/api/generate \
  -H "Content-Type: application/json" \
  -d '{"num_cases": 100}'

# Health check
curl http://localhost:8001/health
```

### 2. Inference Service
```bash
# List available models
curl http://localhost:8004/models

# Predict activity duration
curl -X POST http://localhost:8004/predict/duration \
  -H "Content-Type: application/json" \
  -d '{
    "activity": "Manual Review",
    "customer_tier": "Gold",
    "complexity_score": 7.5,
    "priority": 2
  }'

# Predict SLA breach probability
curl -X POST http://localhost:8004/predict/sla_breach \
  -H "Content-Type: application/json" \
  -d '{
    "activity": "Manual Review",
    "hours_to_sla": 4,
    "complexity_score": 8,
    "customer_tier": "Gold"
  }'
```

### 3. SLA Monitor
```bash
# Get current work-in-progress state
curl http://localhost:8002/state/wip

# Get current bottlenecks
curl http://localhost:8002/bottlenecks/current

# Get SLA breach forecast (next 24 hours)
curl "http://localhost:8002/breaches/forecast?hours=24"

# Get active alerts
curl http://localhost:8002/alerts/active
```

### 4. Simulation Sandbox
```bash
# Get current state snapshot
curl http://localhost:8003/state/snapshot

# Create a scenario (add 3 resources to Review Team)
curl -X POST http://localhost:8003/scenario/create \
  -H "Content-Type: application/json" \
  -d '{"name": "Add 3 to Review", "resource_changes": {"Review Team": 3}}'

# Run simulation and compare
curl -X POST http://localhost:8003/scenario/compare \
  -H "Content-Type: application/json" \
  -d '{"scenario_id": "<scenario-id>", "horizon_hours": 24, "num_runs": 100}'
```

## 🤖 ML Models

Models are stored in `weights/xgboost/v1/`:

| Model | File | Purpose | Features |
|-------|------|---------|----------|
| **Duration** | `duration_model.json` | Predicts activity completion time | activity, tier, complexity, priority |
| **Routing** | `routing_model.json` | Predicts next activity | current activity, case state |
| **SLA Breach** | `sla_model.json` | Predicts breach probability | hours to SLA, complexity, activity |

Model configuration is defined in `weights/registry.yaml`.

## 📊 Data Flow

```
1. Data Simulator generates events
         ↓
2. Events published to Kafka topic "appian-events"
         ↓
3. SLA Monitor consumes events (background thread)
         ↓
4. Events stored in ClickHouse "events" table
         ↓
5. SLA Monitor queries ClickHouse for WIP state
         ↓
6. Inference Service provides ML predictions
         ↓
7. SLA Monitor forecasts breaches & detects bottlenecks
         ↓
8. Simulation Sandbox runs what-if scenarios
         ↓
9. Demo UI displays results & allows queries
```

## 🎨 Demo UI Features

The interactive demo UI (`demo/index.html`) provides:

### Live Dashboard
- Real-time system metrics
- Active case count
- Events per minute
- Average breach risk
- Risk monitor table

### Manual Predictions
- Duration estimator
- SLA risk analyzer
- Auto-fill sample data

### What-If Sandbox
- Scenario configuration
- Resource pool adjustments
- Impact analysis (baseline vs scenario)

### Database Queries
- **Interactive ClickHouse SQL executor**
- Sample query buttons:
  - Total Events
  - Active Cases
  - SLA Breaches
  - Queue Depths
  - Recent Events
- Write custom SQL queries
- Results displayed in formatted table
- Keyboard shortcut: `Ctrl+Enter` to execute

### Starting the Demo UI
```bash
cd demo
python3 server.py
# Open http://localhost:8090
```

## 🗄️ ClickHouse Schema

The `events` table stores all process events:

```sql
CREATE TABLE events (
    event_id UInt64,
    case_id String,
    activity String,
    status String,
    timestamp DateTime,
    resource String,
    sla_deadline DateTime,
    priority UInt8,
    -- Appian-compatible aliases
    c0 String ALIAS activity,
    c1 String ALIAS status,
    c2 DateTime ALIAS timestamp,
    c3 DateTime ALIAS sla_deadline,
    c4 UInt8 ALIAS priority,
    c5 String ALIAS case_id
) ENGINE = MergeTree()
ORDER BY (case_id, timestamp);
```

### Sample Queries

```sql
-- Total events
SELECT count() FROM events;

-- Active cases (not yet approved/rejected)
SELECT case_id, activity, status, timestamp 
FROM events 
WHERE case_id NOT IN (
    SELECT case_id FROM events 
    WHERE activity IN ('Approve', 'Reject') AND status = 'COMPLETED'
)
ORDER BY timestamp DESC;

-- Queue depths by activity
SELECT activity, count() as queue_depth
FROM events
WHERE status = 'ASSIGNED'
GROUP BY activity
ORDER BY queue_depth DESC;

-- SLA breaches
SELECT case_id, activity, timestamp, sla_deadline
FROM events
WHERE timestamp > sla_deadline;
```

## 🔧 Troubleshooting

### Services Not Starting
```bash
# Check service logs
docker compose logs -f sla-monitor

# Restart a service
docker compose restart sla-monitor

# Check container status
docker compose ps
```

### No Data in ClickHouse
```bash
# 1. Check if consumer is connected
docker compose logs sla-monitor | grep "EventConsumer"

# 2. Restart SLA Monitor if needed
docker compose restart sla-monitor

# 3. Generate fresh data
curl -X POST http://localhost:8001/api/generate \
  -H "Content-Type: application/json" \
  -d '{"num_cases": 50}'

# 4. Wait and verify
sleep 8
docker exec clickhouse clickhouse-client --query "SELECT count() FROM events"
```

### Kafka Connection Issues
```bash
# Check Kafka is running
docker compose ps kafka

# View Kafka topics
docker exec kafka kafka-topics --list --bootstrap-server localhost:9093

# Check consumer group
docker exec kafka kafka-consumer-groups \
  --bootstrap-server localhost:9093 \
  --describe --group sla-monitor-consumer
```

### Demo UI Query Errors
```bash
# 1. Ensure ClickHouse is accessible
curl http://localhost:8123/

# 2. Restart demo server
cd demo
# Stop with Ctrl+C, then:
python3 server.py

# 3. Refresh browser at http://localhost:8090
```

## 🛠️ Development

```bash
# Rebuild a specific service
docker compose build sla-monitor

# Rebuild and restart
docker compose up -d --build sla-monitor

# View logs in real-time
docker compose logs -f sla-monitor

# Stop all services
docker compose down

# Stop and remove volumes (clears data)
docker compose down -v
```

## 📁 Project Structure

```
.
├── services/
│   ├── data_simulator/    # Event generation service
│   ├── sla_monitor/       # SLA monitoring & breach prediction
│   ├── inference/         # ML model serving
│   └── simulation_sandbox/# What-if scenario testing
├── config/
│   ├── clickhouse/        # ClickHouse initialization
│   ├── kafka/             # Kafka configuration
│   └── process/           # Process definition (loan_process.yaml)
├── weights/               # ML model weights
│   ├── xgboost/v1/       # XGBoost models
│   └── registry.yaml     # Model registry
├── demo/                  # Interactive demo UI
│   ├── index.html        # Dashboard
│   ├── server.py         # HTTP server with ClickHouse proxy
│   └── Dockerfile        # Demo container
├── docker-compose.yml     # Service orchestration
└── README.md             # This file
```

## 🎓 Use Cases

### 1. Proactive SLA Management
- Monitor active cases in real-time
- Predict which cases will breach SLA
- Take corrective action before breach occurs

### 2. Process Optimization
- Identify bottlenecks automatically
- Test resource allocation changes
- Measure impact before implementation

### 3. Capacity Planning
- Simulate volume spikes
- Test different staffing levels
- Optimize resource distribution

### 4. Process Mining
- Analyze event logs in ClickHouse
- Discover process patterns
- Identify inefficiencies

## 📝 Environment Variables

Key environment variables (set in `docker-compose.yml`):

- `KAFKA_BOOTSTRAP_SERVERS`: Kafka connection (kafka:9093)
- `CLICKHOUSE_HOST`: ClickHouse host (clickhouse)
- `INFERENCE_URL`: Inference service URL (http://inference:8004)
- `MODEL_REGISTRY_PATH`: Path to model registry YAML

## 🚦 Service Health Checks

All services expose a `/health` endpoint:

```bash
curl http://localhost:8001/health  # Data Simulator
curl http://localhost:8002/health  # SLA Monitor
curl http://localhost:8003/health  # Simulation Sandbox
curl http://localhost:8004/health  # Inference
```

## 📊 Metrics & Monitoring

The SLA Monitor exposes Prometheus metrics at `/metrics`:

```bash
curl http://localhost:8002/metrics
```

Key metrics:
- `queue_depth{activity="Manual Review"}` - Queue size per activity
- `resource_utilization{resource="Agent_007"}` - Utilization per agent

## 🔐 Security Notes

This is a **development/demo setup**. For production:
- Add authentication to all services
- Use TLS/SSL for connections
- Secure Kafka with SASL/SSL
- Implement proper access controls
- Use secrets management for credentials

## 📄 License

This project is for demonstration purposes.
