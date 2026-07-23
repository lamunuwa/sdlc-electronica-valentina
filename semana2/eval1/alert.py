# alert.py
from semana2.eval1.anomaly import AnomalyResult


class ConsoleAlert:
    def process_anomaly(self, anomaly: AnomalyResult) -> None:
        raise NotImplementedError
