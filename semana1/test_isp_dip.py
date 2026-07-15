import pytest

from semana1.solid_isp_dip import BadSensorUse, GoodSensorUse, Readable, Writable

# Test de ISP


def test_isp_bad() -> None:
    sensor = BadSensorUse("sensor1")

    reading = sensor.read()

    assert reading.sensor_id == "sensor1"
    assert reading.value == 32.0

    with pytest.raises(NotImplementedError, match="Este sensor no tiene escritura"):
        sensor.write(25.0)

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

    client_write(sensor, value=25.0)

    assert client_read(sensor) == 25.0
