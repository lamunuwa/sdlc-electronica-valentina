from dataclasses import dataclass


@dataclass(frozen=True)
class SensorLimits:
    """Crea los limites fisicos y unidades permitidas para un tipo de sensor"""

    min_value: float
    max_value: float
    units: tuple[str, ...]


limits: dict[str, SensorLimits] = {
    "TEMPERATURE": SensorLimits(min_value=-273.15, max_value=1.416808e32, units=("C", "F", "K"))
    # "HUMIDITY": SensorLimits(...)
    # "PRESSURE": SensorLimits(...)
}

default_unit: dict[str, str] = {
    "TEMPERATURE": "C",
    # "HUMIDITY": "%"
    # "PRESSURE": "Pa"
}


def get_limit(sensor_type: str) -> SensorLimits | None:
    """Busca la configuracion para "sensor_type" y devuelve "None" si no existen"""

    return limits.get(sensor_type)


def validate_reading(sensor_type: str, value: float) -> bool:
    """Evalua un valor recibido y decide si el valor esta dentro del limite"""

    limit = get_limit(sensor_type)
    if limit is None:
        return True
    return limit.min_value <= value <= limit.max_value


def validate_unit(sensor_type: str, unit: str) -> bool:
    """Evalua un tipo y una unidad, devuelve si la unidad es correcta o no existen algo definido"""

    limit = get_limit(sensor_type)
    if limit is None:
        return True
    return unit in limit.units
