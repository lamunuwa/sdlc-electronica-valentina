"""Esquemas Pydantic de entrada y salida para sensores."""

from pydantic import BaseModel, ConfigDict, Field


class SensorCreate(BaseModel):
    """Representa lo que se necesita para registrar un sensor"""

    name: str = Field(..., examples=["TEMP-01"], description="Nombre unico del sensor")
    type: str = Field(..., examples=["TEMPERATURE"], description="Magnitud que mide el sensor")
    unit: str = Field(..., examples=["C"], description="Unidad de medida")


class SensorUpdate(BaseModel):
    """Representa los cambios opcionales que pueden aplicarse a un sensor"""

    name: str | None = Field(None, examples=["TEMP-01"], description="Nombre unico del sensor")
    type: str | None = Field(None, examples=["TEMPERATURE"], description="Nueva magnitud")
    unit: str | None = Field(None, examples=["C"], description="Nueva unidad de medida")


class SensorResponse(BaseModel):
    """Muestra un sensor registrado en la API"""

    id: int
    name: str
    type: str
    unit: str
    active: bool

    model_config = ConfigDict(from_attributes=True)
