import pytest

from semana1.solid_isp_dip import (
    BadDataProcessor,
    BadSensorUse,
    DataProcessor,
    GoodSensorUse,
    InMemoryRepository,
    Readable,
    SensorReading,
    Writable,
)

# Test de ISP


def test_isp_bad() -> None:
    sensor = BadSensorUse("sensor1")

    reading = sensor.read()

    assert reading.sensor_id == "sensor1"
    assert reading.value == 32.0

    with pytest.raises(NotImplementedError, match="Este sensor no tiene escritura"):
        sensor.write(65.0)

    with pytest.raises(NotImplementedError, match="Este sensor no tiene calibracion"):
        sensor.calibrate()

    with pytest.raises(NotImplementedError, match="Este sensor no tiene boton de reset"):
        sensor.reset()


def test_isp_good() -> None:
    def client_read(sensor: Readable) -> float:
        return sensor.read().value

    def client_write(sensor: Writable, value: float) -> None:
        sensor.write(value)

    sensor = GoodSensorUse("sensor1")

    valor_leido = client_read(sensor)
    assert valor_leido == 32.0

    client_write(sensor, value=65.0)

    assert client_read(sensor) == 65.0


# test de DIP


def test_dip_bad(tmp_path) -> None:
    tmp_file = tmp_path / "database.txt"

    processor = BadDataProcessor(filename=str(tmp_file))
    reading = SensorReading("sensor1", 32.0)

    processor.process(reading)

    assert tmp_file.exists()
    assert tmp_file.read_text() == "sensor1: 32.0\n"


def test_dip_good() -> None:
    """Demuestra DIP usando InMemoryRepository para tests"""

    # Usamos repositorio en memoria para testing
    repo = InMemoryRepository()
    processor = DataProcessor(repo)

    # Procesamos una lectura
    processor.process_reading("sensor1", 32.0)

    # Verificamos que se guardó correctamente
    result = processor.get_sensor_reading("sensor1")
    assert result is not None
    assert result.sensor_id == "sensor1"
    assert result.value == 32.0

    # Podemos procesar múltiples lecturas
    processor.process_reading("sensor2", 65.0)
    result2 = processor.get_sensor_reading("sensor2")
    assert result2 is not None
    assert result2.sensor_id == "sensor2"
    assert result2.value == 65.0
