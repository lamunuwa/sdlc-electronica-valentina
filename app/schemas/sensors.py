from pydantic import BaseModel, ConfigDict, Field, field_validator


class SensorThreshold(BaseModel):
    """Representa los datos de umbral configurables de un sensor"""

    min: float | None = Field(
        None,
        examples=[-20.0],
        description="Valor minimo para activar la alarma",
    )
    max: float | None = Field(
        None,
        examples=[40.0],
        description="Valor maximo para activar la alarma",
    )

    @field_validator("min", "max", mode="before")
    @classmethod
    def empty_value_as_none(cls, value: object) -> object:
        return None if value == "" else value


class SensorCreate(BaseModel):
    """Representa lo que se necesita para registrar un sensor"""

    name: str = Field(..., examples=["TEMP-01"], description="Nombre unico del sensor")
    type: str = Field(..., examples=["TEMPERATURE"], description="Magnitud que mide el sensor")
    unit: str = Field(..., examples=["C"], description="Unidad de medida")
    sensor_umbral: SensorThreshold = Field(..., description="Umbral configurado para el sensor")
    ubication: str = Field(..., examples=["Bodega Sur"], description="Ubicacion del sensor")


class SensorUpdate(BaseModel):
    """Representa los cambios opcionales que pueden aplicarse a un sensor"""

    name: str | None = Field(None, examples=["TEMP-01"], description="Nombre unico del sensor")
    type: str | None = Field(None, examples=["TEMPERATURE"], description="Nueva magnitud")
    unit: str | None = Field(None, examples=["C"], description="Nueva unidad de medida")
    sensor_umbral: SensorThreshold | None = Field(
        None, description="Umbral configurable para actualizar"
    )
    ubication: str | None = Field(
        None, examples=["Bodega Sur"], description="Nueva ubicacion del sensor"
    )


class SensorResponse(BaseModel):
    """Muestra un sensor registrado en la API"""

    id: int
    name: str
    type: str
    unit: str
    sensor_umbral: SensorThreshold
    ubication: str
    active: bool

    model_config = ConfigDict(from_attributes=True)
