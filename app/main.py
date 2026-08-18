from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.routers import alerts, health, readings, sensors

tags_metadata = [
    {
        "name": "SENSORS",
        "description": "Operaciones para el manejo de inventario de sensores.",
    },
    {
        "name": "READINGS",
        "description": "Registro y consultas de lecturas de sensores.",
    },
    {
        "name": "ALERTS",
        "description": "Consultas y status de alertas generadas por sensores.",
    },
]

app = FastAPI(
    title="SensorHub API",
    version="0.5.2",
    openapi_tags=tags_metadata,
)

app.include_router(health.router)
app.include_router(sensors.router)
app.include_router(readings.router)
app.include_router(alerts.router)


@app.get("/", include_in_schema=False)
async def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")
