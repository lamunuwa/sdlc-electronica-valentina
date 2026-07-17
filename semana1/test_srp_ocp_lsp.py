import pytest

from semana1.solid_srp_ocp_lsp import (
    BadAnomalyDetector,
    BadHumiditySensor,
    BadSensorReader,
    BadTemperatureSensor,
    DatabaseLogger,
    FileAlert,
    GoodAnomalyDetector,
    GoodHumiditySensor,
    GoodSensorReader,
    GoodTemperatureSensor,
    SensorReading,
    bad_process_sensor,
    process_sensor,
)

# Test de SRP


def test_srp_bad(tmp_path) -> None:
    tmp_file = tmp_path / "log.txt"
    bad_sensor = BadSensorReader(sensor_id="sensor1", filename=str(tmp_file))
    reading = bad_sensor.read_sensor()

    assert reading.sensor_id == "sensor1"
    assert reading.value == 32.0

    bad_sensor.save_to_database(reading)

    assert tmp_file.exists()
    assert tmp_file.read_text() == "sensor1: 32.0\n"


def test_srp_good(tmp_path) -> None:
    tmp_file = tmp_path / "log.txt"
    good_sensor = GoodSensorReader(sensor_id="sensor2")
    reading = good_sensor.read_sensor()

    assert reading.sensor_id == "sensor2"
    assert reading.value == 32.0

    logger = DatabaseLogger(filename=str(tmp_file))
    logger.save(reading)

    assert tmp_file.exists()
    assert tmp_file.read_text() == "sensor2: 32.0\n"


# Test de OCP


def test_ocp_bad(capsys) -> None:
    detector = BadAnomalyDetector(threshold=50.0)
    reading = SensorReading(sensor_id="temperature", value=65.0)

    detector.check(reading, alert="console")

    captured = capsys.readouterr()  # capsys captura lo que se imprimió en la terminal
    assert "Alerta: Anomalia en temperature con valor 65.0" in captured.out


# test_ocp_good se puede realizar con FileAlert o con ConsoleAlert, lo hice con FileAlert
# por que pide 2 test por codigo, yo lo hice como test para la version que no cumple SOLID y
# test que si cumple SOLID, entonces con uno es suficiente y cumple el requisito.
def test_ocp_good(tmp_path) -> None:
    tmp_file = tmp_path / "alert.txt"

    archivo_alerta = FileAlert(filename=str(tmp_file))

    detector = GoodAnomalyDetector(alert=archivo_alerta, threshold=50.0)
    reading = SensorReading(sensor_id="sensor1", value=65.0)

    detector.check(reading)

    assert tmp_file.exists()
    assert tmp_file.read_text() == "Alerta: Anomalia en sensor1 con valor 65.0\n"


# Test de LSP


def test_lsp_bad() -> None:
    temp_sensor = BadTemperatureSensor()
    reading_temp = bad_process_sensor(temp_sensor)
    assert reading_temp.sensor_id == "temperature"

    hum_sensor = BadHumiditySensor()

    with pytest.raises(AttributeError):
        bad_process_sensor(hum_sensor)


def test_lsp_good() -> None:
    temp_sensor = GoodTemperatureSensor()
    hum_sensor = GoodHumiditySensor()

    reading_temp = process_sensor(temp_sensor)
    assert isinstance(reading_temp, SensorReading)
    assert reading_temp.sensor_id == "temperature"
    assert reading_temp.value == 32.0

    reading_hum = process_sensor(hum_sensor)
    assert isinstance(reading_hum, SensorReading)
    assert reading_hum.sensor_id == "humidity"
    assert reading_hum.value == 65.0
