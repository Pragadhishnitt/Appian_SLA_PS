from fastapi import FastAPI, BackgroundTasks, Response
from fastapi.middleware.cors import CORSMiddleware
from app.generator import DataGenerator
from app.kafka_producer import EventProducer
from app.schemas import GenerationRequest
from app.metrics import (
    data_generation_requests, events_generated, cases_generated,
    kafka_publish_duration, get_metrics, get_content_type
)
from datetime import datetime
import time

app = FastAPI(title="Appian Data Simulator")

# Enable CORS for demo UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

generator = DataGenerator()
producer = EventProducer()

@app.on_event("startup")
async def startup_event():
    producer.connect()

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/metrics")
def prometheus_metrics():
    """Prometheus metrics endpoint"""
    return Response(content=get_metrics(), media_type=get_content_type())

@app.post("/api/generate")
async def generate_data(request: GenerationRequest, background_tasks: BackgroundTasks):
    """Generate events and send to Kafka in background"""
    data_generation_requests.inc()
    
    start_date = request.start_date or datetime.now()
    
    cases = generator.generate_cases(request.num_cases, start_date)
    events = generator.generate_events(cases)
    
    # Update metrics
    cases_generated.inc(len(cases))
    events_generated.inc(len(events))
    
    # Send to Kafka in background
    background_tasks.add_task(send_events_to_kafka, events)
    
    return {
        "message": f"Generating {len(events)} events for {request.num_cases} cases",
        "case_count": len(cases),
        "event_count": len(events)
    }

def send_events_to_kafka(events):
    for event in events:
        start_time = time.time()
        producer.send_event(event)
        kafka_publish_duration.observe(time.time() - start_time)
    print(f"Sent {len(events)} events to Kafka")
