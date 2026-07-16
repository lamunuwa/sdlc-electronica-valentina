from dataclasses import dataclass


@dataclass(frozen=True)
class ModbusFrame:
    address: int
    function: int
    data: bytes
    raw_data: bytes
    crc: int
    crc_valid: bool

    min_adress = 1
    max_adress = 247

    @property
    def valid(self) -> bool:
        return self.crc_valid and self.min_adress <= self.address <= self.max_adress

    def to_dict(self) -> dict:
        return {
            "address": self.address,
            "function": self.function,
            "data": self.data,
            "crc": self.crc,
            "crc_valid": self.valid,
        }


class ModBusParser:
    min_length = 4
    max_address = 247

    min_function = 0x01
    max_function = 0x10

    min_exception = 0x81
    max_exception = 0x90

    def can_parse(self, data: bytes) -> bool:
        if len(data) < self.min_length:
            return False

        if not (1 <= data[0] <= self.max_address):
            return False

        standard = self.min_function <= data[1] <= self.max_function
        exception = self.min_exception <= data[1] <= self.max_exception
        if not (standard or exception):
            return False

        return True

    def calculate_crc(self, data: bytes) -> int:
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
        return crc

    def parse(self, data: bytes) -> ModbusFrame | None:
        if not self.can_parse(data):
            return None

        total_len = len(data)
        crc_len = 2

        address = data[0]
        function = data[1]
        payload = data[2 : total_len - crc_len]

        received_crc = int.from_bytes(data[total_len - crc_len : total_len], "little")
        crc_data = data[: total_len - crc_len]
        crc = self.calculate_crc(crc_data)

        return ModbusFrame(
            address=address,
            function=function,
            data=payload,
            raw_data=data,
            crc=received_crc,
            crc_valid=(crc == received_crc),
        )
