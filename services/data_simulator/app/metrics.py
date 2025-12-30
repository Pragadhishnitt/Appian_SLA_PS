from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Metrics
data_generation_requests = Counter(
    'data_generation_requests_total',
    'Total number of data generation requests'
)

events_generated = Counter(
    'events_generated_total',
    'Total number of events generated'
)

cases_generated = Counter(
    'cases_generated_total',
    'Total number of cases generated'
)

kafka_publish_duration = Histogram(
    'kafka_publish_duration_seconds',
    'Time spent publishing to Kafka',
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

def get_metrics():
    """Return Prometheus metrics"""
    return generate_latest()

def get_content_type():
    return CONTENT_TYPE_LATEST
