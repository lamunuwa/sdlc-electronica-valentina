from typing import Any

from semana1.uart_driver.config import UartConfig
from semana1.uart_driver.parsers import MessageParser


class UartDevice:
    def __init__(self, config: UartConfig, parser: MessageParser):
        self.config = config
        self.parser = parser
        self.connection = False
        self.buffer: list[bytes] = []

    def connect(self) -> None:
        self.connection = True
        self.buffer.clear()

    def disconnect(self) -> None:
        self.connection = False
        self.buffer.clear()

    def simulate_data(self, data: bytes) -> None:
        if not self.connection:
            raise ConnectionError("Puerto UART está cerrado")
        self.buffer.append(data)

    def uart_proccess(self) -> Any | None:
        if not self.connection:
            raise RuntimeError("El dispositivo está desconectado")

        if not self.buffer:
            return None

        raw_data = self.buffer[0]
        del self.buffer[0]

        return self.parser.parse(raw_data)
