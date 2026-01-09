import os
from typing import Generator

class Request:
    timestamp: int
    object_id: int
    object_size: int
    response_time: float
    
    def __init__(self, timestamp: int = 0, object_id: int = 0, object_size: int = 0, response_time: float = 0):
        self.timestamp = timestamp
        self.object_id = object_id
        self.object_size = object_size
        self.response_time = response_time
    
    @classmethod
    def from_line(cls, line: str):
        if '\t' in line:
            parts = line.split('\t')
        else:
            parts = line.split(',')
        return cls(int(parts[0]), int(parts[1]), int(parts[2]), float(parts[3]) if len(parts) > 3 else 0)
    
    def __repr__(self):
        return f"Request(timestamp={self.timestamp}, object_id={self.object_id}, object_size={self.object_size}, response_time={self.response_time})"
        

class TrafficReader:
    def __init__(self, model_id: str):
        self.model_id = model_id
        self.model_path = f"{os.path.dirname(__file__)}/models/{model_id}/gen_sequence.txt"
        self._file = None

    def request_count(self) -> int:
        """Get the total number of requests by counting newlines in chunks."""
        count = 0
        with open(self.model_path, 'rb') as f:
            while True:
                buffer = f.read(1024 * 1024)
                if not buffer:
                    break
                count += buffer.count(b'\n')
        return count
    
    def read_traffic(self) -> Generator[Request, None, None]:
        """Read traffic data from the model file line by line."""
        with open(self.model_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    yield Request.from_line(line)
