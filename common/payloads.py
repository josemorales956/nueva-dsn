# common/payloads.py
from dataclasses import dataclass, asdict
import json, time, zlib

FRAME_SEP = b"|CRC:"

@dataclass
class SensorPacket:
    node_id: str
    timestamp: float
    data: dict
    seq: int

    def to_bytes(self) -> bytes:
        raw = json.dumps(asdict(self), separators=(",", ":")).encode("utf-8")
        crc = zlib.crc32(raw)
        return raw + FRAME_SEP + str(crc).encode("utf-8")

    @staticmethod
    def from_bytes(buf: bytes) -> "SensorPacket":
        try:
            raw, crc_part = buf.split(FRAME_SEP, 1)
        except ValueError:
            raise ValueError("bad frame: separator missing")
        calc = zlib.crc32(raw)
        try:
            got = int(crc_part.decode("utf-8"))
        except Exception:
            raise ValueError("bad frame: crc not int")
        if calc != got:
            raise ValueError("crc mismatch")
        payload = json.loads(raw.decode("utf-8"))
        return SensorPacket(**payload)


def make_fake_packet(node_id: str, seq: int) -> SensorPacket:
    # tweak this as you add real sensors
    return SensorPacket(
        node_id=node_id,
        timestamp=time.time(),
        data={"temp_c": 24.5 + (seq % 5) * 0.1, "noise_db": 42.0},
        seq=seq,
    )
