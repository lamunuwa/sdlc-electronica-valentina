from datetime import datetime

from pydantic import BaseModel, ConfigDict


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


class AlertStateUpdate(BaseModel):
    """Esquema para actualizar el estado de una alerta"""

    state: str | None = None
