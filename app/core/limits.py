from dataclasses import dataclass


@dataclass(frozen=True)
class SensorLimits:
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
    return limits.get(sensor_type)


def validate_reading(sensor_type: str, value: float) -> bool:
    limit = get_limit(sensor_type)
    if limit is None:
        return True
    return limit.min_value <= value <= limit.max_value


def validate_unit(sensor_type: str, unit: str) -> bool:
    limit = get_limit(sensor_type)
    if limit is None:
        return True
    return unit in limit.units
