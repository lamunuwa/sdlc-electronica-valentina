from semana1.reading_func.func import (
    Reading,
    SensorType,
    apply_calibration_offset,
    convert_to_fahrenheit,
    format_alert_message,
    is_critical_level,
    to_dict,
)


def test_convert_to_fahrenheit():
    reading_temp = Reading(sensor_id="sensor_1", value=0.0, sensor_type=SensorType.TEMPERATURE)
    assert convert_to_fahrenheit(reading_temp) == 32.0  # Es el valor de 0 grados en Fahrenheit

    reading_hum = Reading(sensor_id="sensor_2", value=50.0, sensor_type=SensorType.HUMIDITY)
    assert convert_to_fahrenheit(reading_hum) == 50.0  # Como es de humedad no altera el valor


# Como en func.py ya devuelve un valor bool, no debemos poner == True/False, es una mala practica
def test_is_critical_level():
    reading = Reading(sensor_id="sensor_1", value=75.0, sensor_type=SensorType.TEMPERATURE)
    assert is_critical_level(reading, max_threshold=70.0)  # Deberia ser critico
    assert not is_critical_level(reading, max_threshold=80.0)  # No deberia ser critico


def test_to_dict():
    reading = Reading(sensor_id="sensor_1", value=25.0, sensor_type=SensorType.TEMPERATURE)
    expected_dict = {"sensor_id": "sensor_1", "value": 25.0, "type": "TEMPERATURE"}
    assert to_dict(reading) == expected_dict


def test_apply_calibration_offset():
    reading = Reading(sensor_id="sensor_1", value=20.0, sensor_type=SensorType.TEMPERATURE)
    offset = 2.5
    cal_reading = apply_calibration_offset(reading, offset)
    assert cal_reading.value == 22.5  # El valor deberia ser el original mas el offset
    assert cal_reading.sensor_id == reading.sensor_id  # El sensor_id deberia permanecer igual
    assert cal_reading.sensor_type == reading.sensor_type  # El tipo de sensor permanece igual


def test_format_alert_message():
    reading = Reading(sensor_id="sensor_1", value=100.0, sensor_type=SensorType.TEMPERATURE)
    reason = "El valor excedio el umbral"
    expected_message = "Alerta: El sensor_1 (TEMPERATURE) reporto un valor inesperado: 100.00. Razon: El valor excedio el umbral"  # noqa: E501
    assert format_alert_message(reading, reason) == expected_message
