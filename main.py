import time
import uuid
from typing import List
from fastapi import FastAPI, Query, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

ALLOWED_ORIGIN = "https://dash-xfs84l.example.com"
MY_EMAIL = "22f1001623@ds.study.iitm.ac.in"

class StatsResponse(BaseModel):
    email: str
    count: int
    sum: int
    min: int
    max: int
    mean: float

@app.middleware("http")
async def strict_cors_and_metrics_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    request_id = str(uuid.uuid4())
    
    # Extract incoming Origin safely
    origin = request.headers.get("origin") or request.headers.get("Origin")

    # 1. Handle Preflight (OPTIONS) Requests cleanly
    if request.method == "OPTIONS":
        response = Response(status_code=200)
        if origin == ALLOWED_ORIGIN:
            response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
            response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "*"
            response.headers["Access-Control-Max-Age"] = "86400"
        
        # Add required custom tracking headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{time.perf_counter() - start_time:.6f}"
        return response

    # 2. Handle Actual Processing Requests (GET)
    try:
        response = await call_next(request)
    except Exception:
        response = JSONResponse(status_code=500, content={"detail": "Internal server error"})

    # Apply strict CORS matching logic on runtime responses
    if origin == ALLOWED_ORIGIN:
        response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN

    # Inject required application performance metrics
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{time.perf_counter() - start_time:.6f}"
    
    return response

@app.get("/stats", response_model=StatsResponse)
async def get_stats(values: str = Query(..., description="Comma-separated integers")):
    try:
        raw_list = [x.strip() for x in values.split(",") if x.strip()]
        if not raw_list:
            return JSONResponse(status_code=400, content={"detail": "Empty values list"})
            
        int_values: List[int] = [int(x) for x in raw_list]
        
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
        return JSONResponse(status_code=400, content={"detail": "Invalid integer format"})
