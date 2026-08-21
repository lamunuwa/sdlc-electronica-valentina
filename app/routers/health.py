import os
import time
from datetime import datetime

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db import get_db

router = APIRouter(tags=["HEALTH"])

START = time.time()
VERSION = os.getenv("SensorHub", "1.0.0")


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check(db: Session = Depends(get_db)) -> JSONResponse:  # noqa: B008
    """Verifica la salud del servicio y la conectividad con dependencias críticas."""

    uptime = round(time.time() - START, 2)

    db_status = "healthy"
    db_latency = None

    try:
        start_db_time = time.perf_counter()
        db.execute(text("SELECT 1"))
        db_latency = round((time.perf_counter() - start_db_time) * 1000, 2)
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    is_healthy = db_status == "healthy"
    global_status = "ok" if is_healthy else "degraded"

    payload = {
        "status": global_status,
        "version": VERSION,
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": uptime,
        "checks": {
            "database": {
                "status": db_status,
                "latency": db_latency,
            }
        },
    }

    status_code = status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(content=payload, status_code=status_code)
