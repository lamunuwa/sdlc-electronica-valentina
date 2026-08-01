from datetime import datetime

from semana2.eval1.anomaly import (
    AnomalyDetector,
    AnomalyType,
    ThresholdConfigManager,
)
from semana2.eval1.reading import SensorReading


def test_detectar_anomalia_por_alta_temperatura() -> None:
    # Given: umbral maximo de temperatura 35.0 °C
    config_manager = ThresholdConfigManager()
    config_manager.configure_threshold(
        sensor_id="TEMP-01", max_value=35.0, anomaly_type=AnomalyType.HIGH_TEMPERATURE
    )
    detector = AnomalyDetector(config_manager)

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
    config_manager = ThresholdConfigManager()
    config_manager.configure_threshold(
        sensor_id="TEMP-01", max_value=35.0, anomaly_type=AnomalyType.HIGH_TEMPERATURE
    )
    detector = AnomalyDetector(config_manager)

    # And: una lectura del sensor "TEMP-01" con temperatura 22.0
    reading = SensorReading(sensor_id="TEMP-01", value=22.0, timestamp=datetime.now())

    # When: el detector evalua la lectura
    result = detector.evaluate(reading)

    # Then: el resultado indica que no hay anomalia
    assert result.is_anomaly is False


def test_valor_exactamente_en_el_umbral_no_se_considera_anomalia() -> None:
    # Given: umbral maximo de temperatura 35.0 °C
    config_manager = ThresholdConfigManager()
    config_manager.configure_threshold(
        sensor_id="TEMP-01", max_value=35.0, anomaly_type=AnomalyType.HIGH_TEMPERATURE
    )
    detector = AnomalyDetector(config_manager)

    # And: una lectura del sensor "TEMP-01" con temperatura 35.0
    reading = SensorReading(sensor_id="TEMP-01", value=35.0, timestamp=datetime.now())

    # When: el detector evalua la lectura
    result = detector.evaluate(reading)

    # Then: el resultado indica que no hay anomalia
    assert result.is_anomaly is False


def test_configurar_umbrales_para_tipo_de_sensor_especifico() -> None:
    # Given: un sistema de monitoreo sin umbrales
    config_manager = ThresholdConfigManager()

    # When: configuro un umbral maximo de 15.0 cm para un sensor "ULTRASONIC-01"
    threshold_config = config_manager.configure_threshold(
        sensor_id="ULTRASONIC-01", max_value=15.0, anomaly_type=AnomalyType.TOO_FAR
    )

    # Then: el sistema almacena la regla de umbral para "ULTRASONIC-01"
    assert threshold_config is not None
    assert threshold_config.sensor_id == "ULTRASONIC-01"
    # And: el umbral limite es configurado en 15.0 cm
    assert threshold_config.max_value == 15.0
    # And: el tipo de anomalia es TOO_FAR
    assert threshold_config.anomaly_type == AnomalyType.TOO_FAR


def test_detectar_anomalia_usando_umbrales_especificos_del_tipo_de_sensor() -> None:
    # Given: el umbral configurado es de 15.0 cm
    config_manager = ThresholdConfigManager()
    config_manager.configure_threshold(
        sensor_id="ULTRASONIC-01", max_value=15.0, anomaly_type=AnomalyType.TOO_FAR
    )
    detector = AnomalyDetector(config_manager)

    # And: una lectura del sensor "ULTRASONIC-01" con valor de distancia 18.1 cm
    reading = SensorReading(sensor_id="ULTRASONIC-01", value=18.1, timestamp=datetime.now())

    # When: el detector evalua la lectura
    result = detector.evaluate(reading)

    # Then: se detecta la anomalia de tipo TOO_FAR
    assert result.is_anomaly is True
    assert result.anomaly_type == AnomalyType.TOO_FAR
    assert result.sensor_id == "ULTRASONIC-01"
    assert result.value == 18.1
