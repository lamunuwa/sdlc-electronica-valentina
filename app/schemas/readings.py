"""Esquemas Pydantic de entrada y salida para lecturas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReadingCreate(BaseModel):
    """Representa lo que se necesita para registrar una lectura"""

    value: float = Field(..., examples=[10.5], description="Valor de la lectura")
    unit: str = Field(..., examples=["C"], description="Unidad de medida (C, BAR, V, ...)")


class ReadingResponse(BaseModel):
    """Muestra una lectura registrada en la API"""

    id: int
    sensor_id: int
    value: float
    unit: str
    timestamp: datetime
    hash_id: str

    model_config = ConfigDict(from_attributes=True)
