from fastapi import FastAPI, APIRouter
from src.api import api

app = FastAPI(title="Cost Tracker API")
app.include_router(api.router, prefix="/api/v1")
