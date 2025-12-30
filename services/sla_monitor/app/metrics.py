from prometheus_client import Gauge, Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Metrics
sla_breach_probability = Gauge(
    'sla_breach_probability', 
    'Probability of SLA breach for a case',
    ['case_id', 'tier']
)

queue_depth = Gauge(
    'queue_depth',
    'Current queue depth per activity',
    ['activity']
)

resource_utilization = Gauge(
    'resource_utilization',
    'Resource pool utilization',
    ['pool']
)

forecast_requests = Counter(
    'forecast_requests_total',
    'Total forecast requests'
)

forecast_latency = Histogram(
    'forecast_latency_seconds',
    'Forecast request latency'
)

events_consumed = Counter(
    'events_consumed_total',
    'Total events consumed from Kafka'
)

clickhouse_query_duration = Histogram(
    'clickhouse_query_duration_seconds',
    'ClickHouse query execution time',
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0]
)

active_alerts = Gauge(
    'active_alerts',
    'Number of active alerts'
)

sla_breaches_predicted = Counter(
    'sla_breaches_predicted_total',
    'Total number of SLA breaches predicted'
)

active_case_count = Gauge(
    'active_case_count',
    'Number of active cases being monitored'
)

def update_queue_metrics(depths: dict):
    """Update queue depth metrics"""
    for activity, depth in depths.items():
        queue_depth.labels(activity=activity).set(depth)

def update_utilization_metrics(utilization: dict):
    """Update resource utilization metrics"""
    for resource, util in utilization.items():
        resource_utilization.labels(pool=resource).set(util)

def get_metrics():
    """Return Prometheus metrics"""
    return generate_latest()

def get_content_type():
    return CONTENT_TYPE_LATEST
