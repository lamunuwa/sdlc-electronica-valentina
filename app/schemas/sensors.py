from pydantic import BaseModel, ConfigDict, Field


class SensorThreshold(BaseModel):
    """Representa los datos de umbral configurables de un sensor"""

    min: float = Field(
        ...,
        examples=[-20.0],
        description="Valor minimo para activar la alarma",
    )
    max: float = Field(
        ...,
        examples=[40.0],
        description="Valor maximo para activar la alarma",
    )


class SensorCreate(BaseModel):
    """Representa lo que se necesita para registrar un sensor"""

    name: str = Field(..., examples=["TEMP-01"], description="Nombre unico del sensor")
    type: str = Field(..., examples=["TEMPERATURE"], description="Magnitud que mide el sensor")
    unit: str = Field(..., examples=["C"], description="Unidad de medida")
    sensor_umbral: SensorThreshold = Field(..., description="Umbral configurado para el sensor")
    ubication: str = Field(..., examples=["Bodega Sur"], description="Ubicacion del sensor")


class SensorUpdate(BaseModel):
    """Representa el cuerpo completo requerido para actualizar un sensor (PUT)"""

    name: str = Field(..., examples=["TEMP-01"], description="Nombre unico del sensor")
    type: str = Field(..., examples=["TEMPERATURE"], description="Magnitud que mide el sensor")
    unit: str = Field(..., examples=["C"], description="Unidad de medida")
    sensor_umbral: SensorThreshold = Field(..., description="Umbral configurado para el sensor")
    ubication: str = Field(..., examples=["Bodega Sur"], description="Ubicacion del sensor")


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


class SensorStatisticsResponse(BaseModel):
    """Muestra las estadisticas de lecturas de un sensor en un periodo"""

    sensor_id: int
    sensor_name: str
    total_readings: int
    min_value: float
    max_value: float
    avg_value: float
