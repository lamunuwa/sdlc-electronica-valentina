from dataclasses import dataclass


@dataclass(frozen=True)
class SensorLimits:
    """Crea los limites fisicos y unidades permitidas para un tipo de sensor"""

    min_value: float
    max_value: float


limits: dict[str, dict[str, SensorLimits]] = {
    "TEMPERATURE": {
        "C": SensorLimits(min_value=-273.15, max_value=1.416808e32),
        "K": SensorLimits(min_value=0.0, max_value=1.416808e32),
        "F": SensorLimits(min_value=-459.67, max_value=2.550254e32),
    },
    "HUMIDITY": {
        "%": SensorLimits(min_value=0.0, max_value=100),
    },
    "DISTANCE": {
        "KM": SensorLimits(min_value=0.0, max_value=4.40e23),
        "M": SensorLimits(min_value=0.0, max_value=4.40e26),
        "CM": SensorLimits(min_value=0.0, max_value=4.40e26),
    },
}


def is_type_supported(sensor_type: str) -> bool:
    """Verifica si el tipo de sensor esta registrado"""
    return sensor_type in limits


def is_unit_supported(sensor_type: str, unit: str) -> bool:
    """Verifica si la unidad enviada es valida para el tipo de sensor"""
    if not is_type_supported(sensor_type):
        return False
    return unit in limits[sensor_type]


def is_value_valid(sensor_type: str, unit: str, value: float) -> bool:
    """Verifica si el valor esta dentro del rango fisico"""
    if not is_unit_supported(sensor_type, unit):
        return False
    limit = limits[sensor_type][unit]
    return limit.min_value <= value <= limit.max_value
