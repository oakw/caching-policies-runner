from .base import AdmissionPolicy
from .count_min_sketch import CountMinSketch, default_cms_width_depth
from dataclasses import dataclass

@dataclass
class DoorkeeperCMSAdmission(AdmissionPolicy):
    """
    LFU + Doorkeeper admission.

    Every request increments a counter.
    On a miss, the object is admitted only if its estimated frequency >= threshold,
    preventing one-hits from ruining long-tailed workloads.

    """

    threshold: int = 2
    width: int | None = None
    depth: int | None = None
    epsilon: float = 0.001
    delta: float = 1e-6
    conservative: bool = True

    def __post_init__(self):
        if self.threshold < 1:
            raise ValueError("threshold must be >= 1")

        if self.width is None or self.depth is None:
            w, d = default_cms_width_depth(self.epsilon, self.delta)
            self.width = self.width or w
            self.depth = self.depth or d

        self.cms = CountMinSketch(width=int(self.width), depth=int(self.depth), conservative=self.conservative)

    def on_access(self, key: int, timestamp: int, size: int, hit: bool) -> None:
        self.cms.increment(key, 1)

    def accept(self, key: int, timestamp: int, size: int) -> bool:
        return self.cms.estimate(key) >= self.threshold
