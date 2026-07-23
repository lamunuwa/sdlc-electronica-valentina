from datetime import datetime

from semana2.eval1.anomaly import (
    AnomalyDetector,
    AnomalyType,
)
from semana2.eval1.reading import SensorReading


def test_detectar_anomalia_por_alta_temperatura() -> None:
    # Given: umbral maximo de temperatura 35.0 °C
    detector = AnomalyDetector()

    # And: una lectura del sensor "TEMP-01" con temperatura 36.5
    reading = SensorReading(sensor_id="TEMP-01", value=36.5, timestamp=datetime.now())

    # When: el detector evalua la lectura
    result = detector.evaluate(reading)

    # Then: el resultado indica que hay anomalia
    assert result.is_anomaly is True
    # And: los detalles de la anomalia son correctos
    assert result.anomaly_type == AnomalyType.HIGH_TEMPERATURE
    assert result.sensor_id == "TEMP-01"
    assert result.value == 36.5


def test_normalidad_dentro_de_umbrales() -> None:
    # Given: umbral maximo de temperatura 35.0 °C
    detector = AnomalyDetector()

    # And: una lectura del sensor "TEMP-01" con temperatura 22.0
    reading = SensorReading(sensor_id="TEMP-01", value=22.0, timestamp=datetime.now())

    # When: el detector evalua la lectura
    result = detector.evaluate(reading)

    # Then: el resultado indica que no hay anomalia
    assert result.is_anomaly is False


def test_valor_exactamente_en_el_umbral_no_se_considera_anomalia() -> None:
    # Given: umbral maximo de temperatura 35.0 °C
    detector = AnomalyDetector()

    # And: una lectura del sensor "TEMP-01" con temperatura 35.0
    reading = SensorReading(sensor_id="TEMP-01", value=35.0, timestamp=datetime.now())

    # When: el detector evalua la lectura
    result = detector.evaluate(reading)

    # Then: el resultado indica que no hay anomalia
    assert result.is_anomaly is False
