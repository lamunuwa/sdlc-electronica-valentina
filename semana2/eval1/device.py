from typing import Any

from semana2.eval1.alert import AlertManager
from semana2.eval1.anomaly import AnomalyDetector
from semana2.eval1.gauss_distro import SensorSimulator
from semana2.eval1.reading import ReadingRecorder, SensorReading
from semana2.eval1.registry import SensorRepository


class PipelineModule:
    def __init__(
        self,
        sensor_repository: SensorRepository,
        reading_recorder: ReadingRecorder,
        anomaly_detector: AnomalyDetector,
        alert_manager: AlertManager,
        media: float = 25.0,
        standard: float = 2.0,
        reading_provider: Any = None,
    ) -> None:
        self.sensor_repository = sensor_repository
        self.reading_recorder = reading_recorder
        self.anomaly_detector = anomaly_detector
        self.alert_manager = alert_manager
        self.media = media
        self.standard = standard
        self.reading_provider = reading_provider
        self.simulator: SensorSimulator | None = None

    def get_readings_from_simulator(self) -> list[SensorReading]:
        raise NotImplementedError

    def run_1_cycle(self) -> None:
        raise NotImplementedError

    def run_cycles(self, cycles: int) -> None:
        raise NotImplementedError
