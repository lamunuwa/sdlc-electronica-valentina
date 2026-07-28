from fastapi import FastAPI, status

from app.db import Base, engine
from app.routers import sensors

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SensorHub API", version="0.1.0")

app.include_router(sensors.router)


@app.get("/health", status_code=status.HTTP_200_OK)
def health() -> dict[str, str]:
    return {"status": "ok"}
