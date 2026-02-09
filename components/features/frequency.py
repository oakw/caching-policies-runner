import math
from .base import Feature

class FrequencyFeature(Feature):
    def __init__(self):
        self.access_times: dict[int, list[int]] = {}

    def on_access(self, key, timestamp, size: int = 0, latency: float = 0.0):
        self.access_times.setdefault(key, []).append(timestamp)

    def value(self, key):
        return len(self.access_times.get(key, []))

    def recent_count(self, key, now, window):
        """Return the number of accesses for `key` within [now - window, now].
        This scans the timestamp list and counts timestamps >= now - window.
        """
        times = self.access_times.get(key, [])
        if not times:
            return 0
        threshold = now - window

        count = 0
        for t in reversed(times):
            if t >= threshold:
                count += 1
            else:
                break
        return count

    def decayed_frequency(self, key, now, tau):
        """Continuous exponential decay of frequency.
        Returns sum(exp(-(now - t)/tau)) over all access timestamps for key.
        """
        times = self.access_times.get(key, [])

        if not times:
            return 0.0
        total = 0.0

        for t in times:
            dt = now - t
            if dt < 0:
                dt = 0 # This shouldnt happen though

            total += math.exp(-(dt / tau))

        return total

