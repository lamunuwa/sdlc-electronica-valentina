from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AlertStateUpdate(BaseModel):
    """Esquema para actualizar el estado de una alerta"""

    state: str | None = Field(
        None, examples=["OPEN, ACKNOWLEDGED, RESOLVED"], description="Nuevo estado de la alerta"
    )


class AlertResponse(BaseModel):
    """Expone una alerta mediante la API"""

    id: int
    sensor_id: int
    reading_id: int
    type: str
    value: float
    unit: str
    state: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
