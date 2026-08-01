from typing import Any

from semana2.eval1.alert import AlertManager
from semana2.eval1.anomaly import AnomalyDetector
from semana2.eval1.gauss_distro import SensorSimulator
from semana2.eval1.reading import ReadingRecorder, SensorReading
from semana2.eval1.registry import SensorRepository


class PipelineModule:
    """Clase madre para los modulos de la pipeline, es decir, todos los modulos de eval1/"""

    def __init__(
        self,
        sensor_repository: SensorRepository,
        reading_recorder: ReadingRecorder,
        anomaly_detector: AnomalyDetector,
        alert_manager: AlertManager,
        # Podria parecer innecesario, y deja al limite la regla DIP, sin embargo el US
        # fue generado con inteligencia artificial por que este modulo no es solicitado
        # como tal en entregables. Y para seguir el US generado debemos insertar media y
        # standard para el ultimo test y reading_provider para los primeros 2.
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
        if self.simulator is None:
            num_sensors = len(self.sensor_repository.sensors)
            if num_sensors == 0:
                raise ValueError("No hay sensores registrados")
            self.simulator = SensorSimulator(
                num_sensores=num_sensors,
                media=self.media,
                desviacion=self.standard,  # Standard hace referencia a la desviacion estandar
            )

        sensor_ids = list(self.sensor_repository.sensors.keys())
        raw_data = self.simulator.ejecutar_simulacion(ciclos=1, intervalo=0)

        return [
            SensorReading(
                sensor_id=sensor_ids[data["sensor_id"]],
                value=data["temperatura"],
                timestamp=data["timestamp"],
            )
            for data in raw_data
        ]

    def run_1_cycle(self) -> None:
        if self.reading_provider:
            readings = self.reading_provider()
        else:
            readings = self.get_readings_from_simulator()

        for r in readings:
            self.reading_recorder.record_reading(r.sensor_id, r.value, r.timestamp)
            result = self.anomaly_detector.evaluate(r)
            if result.is_anomaly:
                self.alert_manager.process_anomaly(result)

    def run_cycles(self, cycles: int) -> None:
        for _i in range(cycles):  # Mypy me obliga a usar _ en lugar de i
            self.run_1_cycle()
