from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time
import uuid

app = FastAPI()

ALLOWED_ORIGIN = "https://dash-xfs84l.example.com"
EMAIL = "22f1001623@ds.study.iitm.ac.in"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_headers(request: Request, call_next):
    start = time.perf_counter()
    request_id = str(uuid.uuid4())

    response = await call_next(request)

    process_time = time.perf_counter() - start
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time:.6f}"
    return response

@app.get("/stats")
async def stats(values: str):
    nums = [int(x.strip()) for x in values.split(",") if x.strip()]

    count = len(nums)
    total = sum(nums)
    minimum = min(nums)
    maximum = max(nums)
    mean = total / count

    return {
        "email": EMAIL,
        "count": count,
        "sum": total,
        "min": minimum,
        "max": maximum,
        "mean": mean,
    }