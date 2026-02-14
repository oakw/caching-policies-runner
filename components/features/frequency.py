import math
from bisect import bisect_left
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
        This bisects the timestamp list to find and count where timestamps >= now - window.
        """
        times = self.access_times.get(key, [])
        if not times:
            return 0
        threshold = now - window

        # Since times are in non-decreasing order,
        # one can use bisect magic to find the cutoff point where
        # times[index] >= threshold and discard everything previously
        if times[0] < threshold:
            idx = bisect_left(times, threshold)
            del times[:idx]

        return len(times)

    def decayed_frequency(self, key, now, tau):
        """Continuous exponential decay of frequency.
        Returns sum(exp(-(now - t)/tau)) over all (mathematically meaningful) access timestamps for key.
        """
        times = self.access_times.get(key, [])

        if not times:
            return 0.0
        total = 0.0

        eps = 1e-12
        for t in reversed(times):
            dt = now - t
            if dt < 0:
                dt = 0 # This shouldnt happen though
            contrib = math.exp(-(dt / tau))
            total += contrib

            # To reduce going through the entire history,
            # stop when contribution becomes uselessly small
            if contrib < eps:
                break

        return total

