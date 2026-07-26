import threading
from typing import Any

from semana1.uart_driver.config import UartConfig
from semana1.uart_driver.parsers import MessageParser
from semana1.uart_driver.recorder import Log


class ThreadSafe:
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.buffer: list[bytes] = []
        self.lock = threading.Lock()

    def enqueue(self, item: bytes) -> bool:
        with self.lock:
            if len(self.buffer) >= self.capacity:
                return False

            self.buffer.append(item)
            return True

    def dequeue(self) -> bytes | None:
        with self.lock:
            if len(self.buffer) == 0:
                return None

            item = self.buffer[0]
            del self.buffer[0]

            return item


class UartDevice:
    def __init__(self, config: UartConfig, parser: MessageParser, buffer_capacity: int):
        self.config = config
        self.parser = parser
        self.connection = False
        self.buffer = ThreadSafe(capacity=buffer_capacity)

    def connect(self) -> None:
        self.connection = True
        Log.log_json("info", "uart_connected", {"baudrate": self.config.baudrate})

    def disconnect(self) -> None:
        self.connection = False
        Log.log_json("info", "uart_disconnected", {"baudrate": self.config.baudrate})

    def simulate_data(self, data: bytes) -> None:
        if not self.connection:
            Log.log_json("error", "write_failed", {"reason": "device_disconnected"})
            raise ConnectionError("Puerto UART esta cerrado")

        complete = self.buffer.enqueue(data)
        if not complete:
            Log.log_json("warning", "buffer_full", {"current_capacity": self.buffer.capacity})
        else:
            Log.log_json("debug", "data_received", {"bytes_count": len(data)})

    def uart_proccess(self) -> Any | None:
        if not self.connection:
            raise RuntimeError("El dispositivo esta desconectado")

        raw_data = self.buffer.dequeue()
        if not raw_data:
            return None

        parsed_msg = self.parser.parse(raw_data)
        if parsed_msg:
            Log.log_json("info", "frame_parsed_pass", {"protocol": type(self.parser).__name__})
        else:
            Log.log_json("warning", "parsing_failed", {"raw_data": raw_data.hex()})

        return parsed_msg
