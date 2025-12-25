import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel as PydanticModel
from typing import Dict, Any, Optional
from app.registry import ModelRegistry

app = FastAPI(title="Inference Service")

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
    result = registry.predict("duration_predictor", features)
    return {"duration_hours": float(result[0]) if hasattr(result, '__getitem__') else float(result)}

@app.post("/predict/routing")
def predict_routing(features: Dict[str, Any]):
    """Predict next activity"""
    if not registry:
        raise HTTPException(status_code=503, detail="Registry not loaded")
    result = registry.predict("routing_predictor", features)
    return {"next_activity": result}

@app.post("/predict/sla_breach")
def predict_sla_breach(features: Dict[str, Any]):
    """Predict SLA breach probability"""
    if not registry:
        raise HTTPException(status_code=503, detail="Registry not loaded")
    result = registry.predict("sla_breach_predictor", features)
    return {"breach_probability": float(result[0]) if hasattr(result, '__getitem__') else float(result)}
