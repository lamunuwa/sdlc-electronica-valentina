import datetime
import random
from pathlib import Path

from semana2.eval1.alert import Alert, AlertManager, FileAlert
from semana2.eval1.anomaly import (
    AnomalyDetector,
    AnomalyResult,
    AnomalyType,
    ThresholdConfigManager,
)
from semana2.eval1.device import PipelineModule
from semana2.eval1.reading import ReadingRecorder, SensorReading
from semana2.eval1.registry import SensorRegistry, SensorRepository, SensorType


# Clases de apoyo -------------------------------------
class ConsoleAlert(Alert):
    """IMPORTANTE: Esta clase para cada test funciona como traer la propia clase
    ConsoleAlert de alert.py, ya que al pasar la anomalia por la consola estamos
    imprimiendo en consola y sumando, hacemos 2 cosas a la vez con una sola clase.
    Claro que se podria hacer de diferentes formas como validando FileAlert, las
    lineas, pero incluye mas codigo, y esto es mucho mas explicito"""

    def __init__(self) -> None:
        self.call_count: int = 0

    def process_anomaly(self, anomaly: AnomalyResult) -> None:
        self.call_count += 1


# -----------------------------------------------------


# Tests -----------------------------------------------
def test_ciclo_sin_anomalias(tmp_path: Path) -> None:
    repo = SensorRepository()
    registry = SensorRegistry(repo)
    recorder = ReadingRecorder(repo)
    threshold_man = ThresholdConfigManager()
    detector = AnomalyDetector(threshold_man)
    alert_man = AlertManager()
    alert_cons = ConsoleAlert()

    tmp_file = tmp_path / "alerts.log"
    alert_man.add_handler(alert_cons)  # ConsoleAlert
    alert_man.add_handler(FileAlert(str(tmp_file)))

    registry.register("TEMP-01", SensorType.TEMPERATURE, "Bodega A")
    threshold_man.configure_threshold("TEMP-01", 35.0, AnomalyType.HIGH_TEMPERATURE)

    read = SensorReading(sensor_id="TEMP-01", value=22.0, timestamp=datetime.datetime.now())

    # Given: un PipelineModule configurado
    pipeline = PipelineModule(
        sensor_repository=repo,
        reading_recorder=recorder,
        anomaly_detector=detector,
        alert_manager=alert_man,
        reading_provider=lambda: [read],
    )

    # When: se ejecuta un ciclo
    pipeline.run_1_cycle()

    # Then: hay una lectura en "TEMP-01"
    assert len(recorder.readings) == 1
    assert recorder.readings[0].sensor_id == "TEMP-01"

    # And: evalua la lectura para verificar que no hay anomalia
    eval = detector.evaluate(recorder.readings[0])
    assert eval.is_anomaly is False

    # And: no existe alerta ninguna
    assert alert_cons.call_count == 0


def test_ciclo_con_anomalia_y_alerta(tmp_path: Path) -> None:
    repo = SensorRepository()
    registry = SensorRegistry(repo)
    recorder = ReadingRecorder(repo)
    threshold_man = ThresholdConfigManager()
    detector = AnomalyDetector(threshold_man)
    alert_man = AlertManager()
    alert_cons = ConsoleAlert()

    tmp_file = tmp_path / "alerts.log"
    alert_man.add_handler(alert_cons)  # ConsoleAlert
    alert_man.add_handler(FileAlert(str(tmp_file)))

    registry.register("TEMP-01", SensorType.TEMPERATURE, "Bodega A")
    threshold_man.configure_threshold("TEMP-01", 35.0, AnomalyType.HIGH_TEMPERATURE)

    read = SensorReading(sensor_id="TEMP-01", value=38.0, timestamp=datetime.datetime.now())

    # Given: un PipelineModule configurado
    pipeline = PipelineModule(
        sensor_repository=repo,
        reading_recorder=recorder,
        anomaly_detector=detector,
        alert_manager=alert_man,
        reading_provider=lambda: [read],
    )

    # When: se ejecuta un ciclo
    pipeline.run_1_cycle()

    # Then: hay una lectura en "TEMP-01"
    assert len(recorder.readings) == 1
    assert recorder.readings[0].sensor_id == "TEMP-01"

    # And: la anomalia es correcta con respecto a la lectura
    eval = detector.evaluate(recorder.readings[0])
    assert eval.is_anomaly is True
    assert eval.anomaly_type == AnomalyType.HIGH_TEMPERATURE
    assert eval.sensor_id == "TEMP-01"
    assert eval.value == 38.0

    # And: el AlertManager notifica una alerta a los canales
    assert alert_cons.call_count == 1

    # And: "alerts.log" refleja la nueva entrada
    assert tmp_file.exists()
    content = tmp_file.read_text()
    assert "TEMP-01" in content
    assert "38.0" in content


def test_simulacion_carga_distribuida_e2e(tmp_path: Path) -> None:
    repo = SensorRepository()
    registry = SensorRegistry(repo)
    recorder = ReadingRecorder(repo)
    threshold_man = ThresholdConfigManager()
    detector = AnomalyDetector(threshold_man)
    alert_man = AlertManager()

    tmp_file = tmp_path / "alerts.log"
    alert_man.add_handler(FileAlert(str(tmp_file)))

    for i in range(1, 11):
        sensor_id = f"TEMP-{i}"
        registry.register(sensor_id, SensorType.TEMPERATURE, f"Bodega {i}")
        threshold_man.configure_threshold(sensor_id, 35.0, AnomalyType.HIGH_TEMPERATURE)

    random.seed(7)  # Podria ser cualquier numero, esto solo sirve para que sea reproducible siempre

    # Given: un PipelineModule configurado
    pipeline = PipelineModule(
        sensor_repository=repo,
        reading_recorder=recorder,
        anomaly_detector=detector,
        alert_manager=alert_man,
        media=22.0,
        standard=5.0,
    )

    # When: el pipeline ejecuta 60 ciclos
    pipeline.run_cycles(60)

    # Then: el ReadingRecorder acumula exactamente 600 lecturas
    assert len(recorder.readings) == 600

    # And: "alerts.log" se crea o actualiza
    assert tmp_file.exists()

    # And: los registros de "alerts.log" es exactamente igual al numero de anomalias
    anomalias_detectadas = sum(
        1 for reading in recorder.readings if detector.evaluate(reading).is_anomaly
    )
    lineas = [line for line in tmp_file.read_text().splitlines() if line.strip()]
    assert len(lineas) == anomalias_detectadas


# -----------------------------------------------------
