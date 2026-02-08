import hashlib
import math
from dataclasses import dataclass

@dataclass
class CountMinSketch:
    """
        Count-Min Sketch with conservative update.
        https://www.geeksforgeeks.org/dsa/count-min-sketch-in-python/ and ChatGPT assistance
    """

    width: int
    depth: int
    conservative: bool = True

    def estimate(self, key: int) -> int:
        return min(self.tables[i][idx] for i, idx in self._indices(key))

    def increment(self, key: int, delta: int = 1) -> int:
        if delta <= 0:
            return self.estimate(key)

        if not self.conservative:
            for i, idx in self._indices(key):
                self.tables[i][idx] += delta
            return self.estimate(key)

        # conservative update
        current = self.estimate(key)
        target = current + delta
        for i, idx in self._indices(key):
            if self.tables[i][idx] < target:
                self.tables[i][idx] = target
        return target

    def __post_init__(self):
        if self.width <= 0 or self.depth <= 0:
            raise ValueError("width and depth must be positive")
        self.tables = [[0] * self.width for _ in range(self.depth)]

    @staticmethod
    def _hash_i(key: int, i: int) -> int:
        # Use deterministic hashing (blake2b) so results are reproducible across runs.
        h = hashlib.blake2b(f"{key}:{i}".encode("utf-8"), digest_size=8)
        return int.from_bytes(h.digest(), "little", signed=False)

    def _indices(self, key: int):
        for i in range(self.depth):
            yield i, self._hash_i(key, i) % self.width


def default_cms_width_depth(epsilon: float = 0.001, delta: float = 1e-6) -> tuple[int, int]:
    """
    Return (width, depth) for given error bounds.
    """
    if epsilon <= 0 or delta <= 0 or delta >= 1:
        raise ValueError("epsilon must be >0 and delta must be in (0,1)")
    # approximate
    width = int(math.ceil(math.e / epsilon))
    depth = int(math.ceil(math.log(1.0 / delta)))
    return width, depth
