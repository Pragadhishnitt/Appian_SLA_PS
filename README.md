# Appian Predictive Simulation MVP

A process mining and predictive simulation platform for Appian workflows. Uses ML to predict activity durations, next activities, and SLA breach risks.

## Architecture

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
```

## Quick Start

```bash
# 0. Copy env.example to .env
cp env.example .env

# 1. Start all services
docker compose up -d --build

# 2. Check services are running
docker compose ps

# 3. Generate test data (50 cases → ~400 events)
curl -X POST http://localhost:8001/api/generate \
  -H "Content-Type: application/json" \
  -d '{"num_cases": 50}'

# 4. Wait for data to flow through (5 seconds)
sleep 5

# 5. Verify data in ClickHouse
docker exec clickhouse clickhouse-client --query "SELECT count() FROM events"
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| Data Simulator | 8001 | Generates realistic process events |
| SLA Monitor | 8002 | Proactive SLA breach prediction |
| Simulation Sandbox | 8003 | What-If scenario testing |
| Inference | 8004 | ML model serving (XGBoost) |
| ClickHouse | 8123 | Event storage |
| Kafka | 29092 | Event streaming |
| Grafana | 3000 | Dashboards (admin/admin) |
| Prometheus | 9090 | Metrics |
| Flink | 8081 | Stream processing (future) |

## Testing the Services

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
```

### 5. Observability
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

## ML Models

Models are stored in `weights/xgboost/v1/`:

| Model | File | Purpose |
|-------|------|---------|
| Duration | `duration_model.json` | Predicts activity completion time |
| Routing | `routing_model.json` | Predicts next activity |
| SLA Breach | `sla_model.json` | Predicts breach probability |


## Data Flow

1. **Data Simulator** generates realistic loan application events
2. Events are sent to **Kafka** topic `appian-events`
3. **SLA Monitor** consumes events and stores in **ClickHouse**
4. **Inference Service** provides ML predictions
5. **SLA Monitor** uses predictions to forecast breaches
6. **Simulation Sandbox** runs what-if scenarios

## Environment Variables

Key environment variables (set in `docker-compose.yml`):
- `KAFKA_BOOTSTRAP_SERVERS`: Kafka connection (kafka:9093)
- `CLICKHOUSE_HOST`: ClickHouse host (clickhouse)
- `INFERENCE_URL`: Inference service URL (http://inference:8004)
- `MODEL_REGISTRY_PATH`: Path to model registry YAML

## Troubleshooting

```bash
# Check service logs
docker compose logs -f [service-name]

# Restart a service
docker compose restart [service-name]

# View Kafka topics
docker exec kafka kafka-topics --list --bootstrap-server localhost:9093

# Query ClickHouse directly
docker exec clickhouse clickhouse-client --query "SELECT * FROM events LIMIT 10"

# Check container status
docker compose ps
```

## Development

```bash
# Rebuild a specific service
docker compose build [service-name]

# Rebuild and restart
docker compose up -d --build [service-name]

# Stop all services
docker compose down

# Stop and remove volumes
docker compose down -v
```
