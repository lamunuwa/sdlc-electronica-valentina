from dataclasses import dataclass
from enum import Enum, auto


class Parity(Enum):
    N = auto()
    E = auto()
    O = auto()  # noqa: E741


class StopBits(Enum):
    One = 1
    Two = 2


@dataclass(frozen=True)
class UartConfig:
    baudrate: int
    parity: Parity
    stop_bits: StopBits
    timeout: float

    def __post_init__(self):
        self.validate_baudrate()
        self.validate_timeout()

    baudrate_group = {9600, 19200, 38400, 57600, 115200}

    def validate_baudrate(self):
        if not isinstance(self.baudrate, int):
            raise TypeError(f"Baudrate incorrecto: {type(self.baudrate).__name__}, debe ser entero")
        if self.baudrate <= 0:
            raise ValueError(f"Baudrate debe ser positivo: {self.baudrate}")
        if self.baudrate not in self.baudrate_group:
            raise ValueError(
                f"Baudrate {self.baudrate} invalido. Lista valida: {self.baudrate_group}"
            )  # noqa: E501

    def validate_timeout(self):
        if self.timeout < 0:
            raise ValueError(f"Timeout no puede ser negativo: {self.timeout}")
