from dataclasses import dataclass, asdict
import json
import time

@dataclass
class SensorPacket:
    node_id: str
    timestamp: float
    data: dict
    seq: int

    def to_json(self):
        return json.dumps(asdict(self))

    @staticmethod
    def from_json(json_str):
        payload = json.loads(json_str)
        return SensorPacket(**payload)
