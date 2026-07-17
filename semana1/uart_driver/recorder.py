import json
from typing import Any


class DataRecorder:
    def __init__(self, output_file: str) -> None:
        self.output_file = output_file
        self.file = None

    def open(self) -> None:
        if self.file is None or self.file.closed:
            self.file = open(self.output_file, "a", encoding="utf-8")  # type: ignore[assignment]

    def record(self, data: dict[str, Any]) -> None:
        if self.file and not self.file.closed:
            self.file.write(json.dumps(data) + "\n")

    def close(self) -> None:
        if self.file and not self.file.closed:
            self.file.close()
