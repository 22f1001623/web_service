import time
import uuid
from typing import List
from fastapi import FastAPI, Query, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

ALLOWED_ORIGIN = "https://dash-xfs84l.example.com"
MY_EMAIL = "22f1001623@ds.study.iitm.ac.in"  # <-- Replace with your actual email

class StatsResponse(BaseModel):
    email: str
    count: int
    sum: int
    min: int
    max: int
    mean: float

@app.middleware("http")
async def process_time_and_cors_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    request_id = str(uuid.uuid4())
    
    # 1. Handle Preflight (OPTIONS) Requests Manually for Strict CORS
    if request.method == "OPTIONS":
        origin = request.headers.get("Origin")
        response = Response(status_code=200)
        
        if origin == ALLOWED_ORIGIN:
            response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
            response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "*"
        
        # Add required custom headers even to preflight
        process_time = time.perf_counter() - start_time
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.6f}"
        return response

    # 2. Handle Actual Requests (GET, etc.)
    response = await call_next(request)
    
    # Enforce strict CORS on the response
    origin = request.headers.get("Origin")
    if origin == ALLOWED_ORIGIN:
        response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN

    # Inject required custom middleware headers
    process_time = time.perf_counter() - start_time
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time:.6f}"
    
    return response

@app.get("/stats", response_model=StatsResponse)
async def get_stats(values: str = Query(..., description="Comma-separated integers")):
    try:
        # Parse the comma-separated integer string
        int_values: List[int] = [int(x.strip()) for x in values.split(",") if x.strip()]
        
        if not int_values:
            return JSONResponse(status_code=400, content={"detail": "No valid integers provided"})
        
        # Compute metrics
        count_val = len(int_values)
        sum_val = sum(int_values)
        min_val = min(int_values)
        max_val = max(int_values)
        mean_val = float(sum_val) / count_val

        return StatsResponse(
            email=MY_EMAIL,
            count=count_val,
            sum=sum_val,
            min=min_val,
            max=max_val,
            mean=round(mean_val, 4)
        )
    except ValueError:
        return JSONResponse(status_code=400, content={"detail": "Invalid integer format in values parameter"})
