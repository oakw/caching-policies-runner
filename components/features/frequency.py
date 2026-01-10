from .base import Feature

class FrequencyFeature(Feature):
    def __init__(self):
        self.access_times: dict[int, list[int]] = {}

    def on_access(self, key, timestamp):
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
