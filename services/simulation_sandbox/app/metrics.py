from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Metrics
simulation_runs = Counter(
    'simulation_runs_total',
    'Total number of simulations executed'
)

simulation_duration = Histogram(
    'simulation_duration_seconds',
    'Time spent running simulations',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

active_scenarios = Gauge(
    'active_scenarios',
    'Number of scenarios currently in memory'
)

def get_metrics():
    """Return Prometheus metrics"""
    return generate_latest()

def get_content_type():
    return CONTENT_TYPE_LATEST
