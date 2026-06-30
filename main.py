from fastapi import FastAPI, Query, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    ALLOWED_ORIGIN = "https://dash-xfs84l.example.com",
    MY_EMAIL = "22f1001623@ds.study.iitm.ac.in",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
ALLOWED_ORIGIN = "https://dash-xfs84l.example.com"
MY_EMAIL = "22f1001623@ds.study.iitm.ac.in"
