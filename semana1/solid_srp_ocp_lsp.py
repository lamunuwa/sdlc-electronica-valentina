from dataclasses import dataclass


@dataclass(frozen=True)
class SensorReading:
    sensor_id: str
    value: float


# S - Single Responsibility Principle: Una clase solo debe tener una razón para cambiar.

# La siguiente clase no sigue el principio de responsabilidad unica, ya que tiene 2
# responsabilidades: lee el sensor y luego escribe un log con la informacion impresa.


class BadSensorReading:
    def __init__(self, sensor_id: str, filename: str = "log.txt") -> None:
        self.sensor_id = sensor_id
        self.filename = filename

    def read_sensor(self) -> SensorReading:
        return SensorReading(sensor_id=self.sensor_id, value=32.0)

    def save_to_database(self, reading: SensorReading) -> None:
        with open(self.filename, "a") as f:
            f.write(f"{reading.sensor_id}: {reading.value}\n")


# La siguiente clase sigue el principio de responsabilidad unica, ya que creamos una clase
# para leer el sensor y otra clase para escribir un log con la informacion impresa.


class GoodSensorReading:
    def __init__(self, sensor_id: str) -> None:
        self.sensor_id = sensor_id

    def read_sensor(self) -> SensorReading:
        return SensorReading(sensor_id=self.sensor_id, value=32.0)


class DatabaseLogger:
    def __init__(self, filename: str) -> None:
        self.filename = filename

    def save(self, reading: SensorReading) -> None:
        with open(self.filename, "a") as f:
            f.write(f"{reading.sensor_id}: {reading.value}\n")
