from pydantic import BaseModel, ConfigDict, Field


class SensorCreate(BaseModel):
    """Clase para la creacion de un nuevo sensor"""

    name: str = Field(..., examples=["TEMP-01"], description="Nombre unico del sensor")
    type: str = Field(..., examples=["TEMPERATURE"], description="Magnitud que mide el sensor")
    unit: str = Field(..., examples=["C"], description="Unidad de medida")


class SensorResponse(BaseModel):
    """Clase para representar un sensor completo"""

    id: int
    name: str
    type: str
    unit: str
    active: bool

    model_config = ConfigDict(from_attributes=True)
