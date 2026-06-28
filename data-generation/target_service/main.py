from fastapi import FastAPI
import time
import random
import math

app = FastAPI(title="Dummy Target Service")

@app.get("/")
def get_root():
    """Simulate a standard, relatively fast endpoint."""
    # Simulate 10-50ms latency
    time.sleep(random.uniform(0.01, 0.05))
    return {"status": "ok", "message": "Normal GET response"}

@app.post("/")
def post_data(payload: dict):
    """Simulate a heavier endpoint that generates CPU load and latency."""
    # Simulate 100-300ms latency
    time.sleep(random.uniform(0.1, 0.3))
    
    # Generate some CPU load
    for i in range(10000):
        math.sqrt(i)
        
    return {"status": "created", "size": len(str(payload))}

@app.get("/health")
def health():
    return {"status": "up"}
