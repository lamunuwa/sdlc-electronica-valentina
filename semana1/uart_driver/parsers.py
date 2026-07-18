from abc import ABC, abstractmethod
from dataclasses import dataclass


class MessageParser(ABC):
    @abstractmethod
    def can_parse(self, data: bytes) -> bool: ...

    @abstractmethod
    def parse(self, data: bytes): ...


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


@dataclass(frozen=True)
class CanFrame:
    id: int
    dlc: int
    data: bytes
    valid: bool

    def to_dict(self) -> dict:
        return {"id": self.id, "dlc": self.dlc, "data": self.data, "valid": self.valid}


@dataclass(frozen=True)
class NMEASentence:
    talker_id: str
    sentence_type: str
    fields: list
    checksum_valid: bool
    raw_sentence: str

    @property
    def valid(self) -> bool:
        """Una sentencia NMEA es válida si pasó el checksum y es del tipo esperado (GGA)"""

        return self.checksum_valid and self.sentence_type == "GGA"

    def to_dict(self) -> dict:
        return {
            "talker_id": self.talker_id,
            "sentence_type": self.sentence_type,
            "fields": self.fields,
            "checksum_valid": self.valid,
            "raw": self.raw_sentence,
        }


class ModBusParser(MessageParser):
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


class CanParser:
    sof = 0x5A

    def can_parse(self, data: bytes) -> bool:
        return len(data) == 12 and data[0] == self.sof

    def parse(self, data: bytes) -> CanFrame | None:
        if not self.can_parse(data):
            return None

        id = int.from_bytes(data[1:3], byteorder="big")
        dlc = data[3]
        payload = data[4 : 4 + dlc]
        valid = dlc <= 8

        return CanFrame(id=id, dlc=dlc, data=payload, valid=valid)


class NMEAParser(MessageParser):
    """Clase para enviar datos en serie y geolocalización NMEA"""

    def can_parse(self, data: bytes) -> bool:
        return data.startswith(b"$") and b"GGA" in data and b"*" in data

    def parse(self, data: bytes) -> NMEASentence | None:
        if not self.can_parse(data):
            return None
        try:
            sentence = data.decode("ascii", errors="ignore").strip()
            content, checksum_str = sentence.rsplit("*", 1)

            calculated_checksum = 0
            for char in content[1:]:
                calculated_checksum ^= ord(char)

            received_checksum = int(checksum_str[:2], 16)
            checksum_valid = calculated_checksum == received_checksum

            fields = content[1:].split(",")
            header = fields[0]

            return NMEASentence(
                talker_id=header[:2],
                sentence_type=header[2:],
                fields=fields[1:],
                checksum_valid=checksum_valid,
                raw_sentence=sentence,
            )
        except Exception:
            return None
