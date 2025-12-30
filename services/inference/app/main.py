import os
import time
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel as PydanticModel
from typing import Dict, Any, Optional
from app.registry import ModelRegistry
from app.metrics import (
    inference_requests, inference_duration, model_load_time,
    prediction_errors, get_metrics, get_content_type
)

app = FastAPI(title="Inference Service")

# Enable CORS for demo UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize registry
REGISTRY_PATH = os.getenv("MODEL_REGISTRY_PATH", "/app/weights/registry.yaml")
registry = None

class PredictionRequest(PydanticModel):
    model_name: str
    version: Optional[str] = None
    features: Dict[str, Any]

class PredictionResponse(PydanticModel):
    model_name: str
    version: str
    prediction: Any

@app.on_event("startup")
async def startup():
    global registry
    if os.path.exists(REGISTRY_PATH):
        registry = ModelRegistry(REGISTRY_PATH)
    else:
        print(f"Warning: Registry not found at {REGISTRY_PATH}")

@app.get("/health")
def health_check():
    return {"status": "healthy", "registry_loaded": registry is not None}

@app.get("/metrics")
def prometheus_metrics():
    """Prometheus metrics endpoint"""
    return Response(content=get_metrics(), media_type=get_content_type())

@app.get("/models")
def list_models():
    """List all available models"""
    if not registry:
        raise HTTPException(status_code=503, detail="Registry not loaded")
    return registry.list_models()

@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    """Run prediction using specified model"""
    if not registry:
        raise HTTPException(status_code=503, detail="Registry not loaded")
    
    try:
        result = registry.predict(
            model_name=request.model_name,
            features=request.features,
            version=request.version
        )
        return PredictionResponse(
            model_name=request.model_name,
            version=request.version or "default",
            prediction=result.tolist() if hasattr(result, 'tolist') else result
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/duration")
def predict_duration(features: Dict[str, Any]):
    """Predict activity duration"""
    if not registry:
        raise HTTPException(status_code=503, detail="Registry not loaded")
    
    model_name = "duration_predictor"
    inference_requests.labels(model_name=model_name).inc()
    
    try:
        start_time = time.time()
        result = registry.predict(model_name, features)
        inference_duration.labels(model_name=model_name).observe(time.time() - start_time)
        return {"duration_hours": float(result[0]) if hasattr(result, '__getitem__') else float(result)}
    except Exception as e:
        prediction_errors.labels(model_name=model_name, error_type=type(e).__name__).inc()
        raise

@app.post("/predict/routing")
def predict_routing(features: Dict[str, Any]):
    """Predict next activity"""
    if not registry:
        raise HTTPException(status_code=503, detail="Registry not loaded")
    
    model_name = "routing_predictor"
    inference_requests.labels(model_name=model_name).inc()
    
    try:
        start_time = time.time()
        result = registry.predict(model_name, features)
        print(f"DEBUG: routing result type: {type(result)}", flush=True)
        print(f"DEBUG: routing result: {result}", flush=True)
        inference_duration.labels(model_name=model_name).observe(time.time() - start_time)
        
        ACTIVITY_NAMES = ["Submit Application", "Check Credit", "Manual Review", 
                          "Quality Assurance", "Approve", "Reject"]
        
        import numpy as np
        if isinstance(result, np.ndarray):
            if result.ndim > 1:
                probs = result[0].tolist()
                pred_idx = int(np.argmax(result[0]))
            else:
                probs = result.tolist()
                pred_idx = int(np.argmax(result))
            
            if len(probs) > 1:
                return {
                    "next_activity": str(ACTIVITY_NAMES[pred_idx]) if pred_idx < len(ACTIVITY_NAMES) else f"Class_{pred_idx}",
                    "predicted_class": pred_idx,
                    "probabilities": [float(p) for p in probs]
                }
            else:
                pred_idx = int(probs[0])
                return {
                    "next_activity": str(ACTIVITY_NAMES[pred_idx]) if pred_idx < len(ACTIVITY_NAMES) else f"Class_{pred_idx}",
                    "predicted_class": pred_idx
                }
        
        # Fallback for non-numpy
        val = result[0] if hasattr(result, '__getitem__') else result
        try:
            pred_idx = int(val)
            return {
                "next_activity": str(ACTIVITY_NAMES[pred_idx]) if 0 <= pred_idx < len(ACTIVITY_NAMES) else str(pred_idx),
                "predicted_class": pred_idx
            }
        except:
            return {"next_activity": str(val)}
    except Exception as e:
        print(f"ERROR in predict_routing: {e}", flush=True)
        prediction_errors.labels(model_name=model_name, error_type=type(e).__name__).inc()
        raise

@app.post("/predict/sla_breach")
def predict_sla_breach(features: Dict[str, Any]):
    """Predict SLA breach probability"""
    if not registry:
        raise HTTPException(status_code=503, detail="Registry not loaded")
    
    model_name = "sla_breach_predictor"
    inference_requests.labels(model_name=model_name).inc()
    
    try:
        start_time = time.time()
        result = registry.predict(model_name, features)
        inference_duration.labels(model_name=model_name).observe(time.time() - start_time)
        return {"breach_probability": float(result[0]) if hasattr(result, '__getitem__') else float(result)}
    except Exception as e:
        prediction_errors.labels(model_name=model_name, error_type=type(e).__name__).inc()
        raise
