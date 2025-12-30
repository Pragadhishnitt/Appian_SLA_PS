from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Metrics
inference_requests = Counter(
    'inference_requests_total',
    'Total number of inference requests',
    ['model_name']
)

inference_duration = Histogram(
    'inference_duration_seconds',
    'Time spent on inference',
    ['model_name'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0]
)

model_load_time = Gauge(
    'model_load_time_seconds',
    'Time taken to load models',
    ['model_name']
)

prediction_errors = Counter(
    'prediction_errors_total',
    'Total number of prediction errors',
    ['model_name', 'error_type']
)

def get_metrics():
    """Return Prometheus metrics"""
    return generate_latest()

def get_content_type():
    return CONTENT_TYPE_LATEST
