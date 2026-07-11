from dataclasses import dataclass
from enum import Enum, auto
from typing import Protocol, Dict, Any

# --- Codigo de ejemplo de la guia de estudios ---

class SensorType(Enum):
    TEMPERATURE = auto()
    HUMIDITY = auto()

@dataclass(frozen=True)
class Reading:
    sensor_id: str
    value: float
    sensor_type: SensorType

class Transport(Protocol):
    def send(self, payload: bytes) -> None: ...

# --- Funciones de reading ---

def convert_to_fahrenheit(r: Reading) -> float: # De celcius a Fahrenheit
    if r.sensor_type == SensorType.TEMPERATURE:
        return (r.value * 9/5) + 32 # Formula estandar de conversion a Fahrenheit
    return r.value

def is_critical_level(r: Reading, max_threshold: float) -> bool: # Deteccion de umbral maximo
    return r.value > max_threshold # Verifica si el valor de la lectura excede el umbral máximo

def to_dict(r: Reading) -> Dict[str, Any]: # Convertir a diccionario, algo que es util para APIs
    return {
        "sensor_id": r.sensor_id,
        "value": r.value,
        "type": r.sensor_type.name  # Por la descripcion, hice algo como una biblioteca
    }

def apply_calibration_offset(r: Reading, offset: float) -> Reading: # Calibracion
    return Reading(
        sensor_id = r.sensor_id,
        value = r.value + offset,
        sensor_type = r.sensor_type # Aprovechamos el frozen class para crear una cota nueva y no modificar la original
    )

def format_alert_message(r: Reading, reason: str) -> str: # Notificaciones
    return f"[ALERT] Sensor {r.sensor_id} ({r.sensor_type.name})reported unexpected value: {r.value:.2f}. Reason: {reason}"