from fastapi import FastAPI

from app.db import Base, engine
from app.routers import health, readings, sensors

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SensorHub API", version="0.3.0")

app.include_router(health.router)
app.include_router(sensors.router)
app.include_router(readings.router)
