import time
import uuid
from fastapi import FastAPI, Request, Response, Query
from fastapi.responses import JSONResponse

app = FastAPI()

# --- CONFIGURATION ---
YOUR_EMAIL = "22f1001623@ds.study.iitm.ac.in"  # FIXME: Change to your exact grader email
ALLOWED_ORIGIN = "https://dash-xfs84l.example.com"

@app.middleware("http")
async def add_custom_headers_and_cors(request: Request, call_next):
    start_time = time.perf_counter()
    
    # 1. Handle Preflight OPTIONS requests strictly
    if request.method == "OPTIONS":
        response = Response(status_code=200)
    else:
        response = await call_next(request)
        
    # 2. Calculate execution time
    process_time = time.perf_counter() - start_time
    
    # 3. Inject Required Middleware Headers
    response.headers["X-Request-ID"] = str(uuid.uuid4())
    response.headers["X-Process-Time"] = f"{process_time:.6f}"
    
    # 4. Enforce Strict, Non-Wildcard CORS Policy
    origin = request.headers.get("origin")
    if origin == ALLOWED_ORIGIN:
        response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
        response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
    # If it's an evil origin, we do NOT add any Access-Control-Allow-Origin header
        
    return response

@app.get("/stats")
async def get_stats(values: str = Query(..., description="Comma-separated integers")):
    try:
        # Parse comma-separated string into integers
        int_list = [int(x.strip()) for x in values.split(",") if x.strip()]
        
        if not int_list:
            return JSONResponse(status_code=400, content={"error": "No valid integers provided"})
        
        # Compute exact descriptive statistics
        count = len(int_list)
        total_sum = sum(int_list)
        minimum = min(int_list)
        maximum = max(int_list)
        mean = total_sum / count
        
        return {
            "email": YOUR_EMAIL,
            "count": count,
            "sum": total_sum,
            "min": minimum,
            "max": maximum,
            "mean": round(mean, 4)  # Securely within the ±0.01 threshold
        }
    except ValueError:
        return JSONResponse(status_code=400, content={"error": "Invalid integer format"})
