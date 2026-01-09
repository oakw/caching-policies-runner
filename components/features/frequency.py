from .base import Feature

class FrequencyFeature(Feature):
    def __init__(self):
        self.counts = {}
        self._sorted_freq_accesses: list[tuple[int, int]] = []

    def on_access(self, key, timestamp):
        previous_count = self.counts.get(key, 0)
        previous_index = self._sorted_freq_accesses.index((key, previous_count)) if previous_count > 0 else -1

        if previous_index != -1:
            self._sorted_freq_accesses.pop(previous_index)

        pushed_forward = False
        for i in range(max(previous_index, 0), len(self._sorted_freq_accesses)):
            if self._sorted_freq_accesses[i][1] > previous_count + 1:
                self._sorted_freq_accesses.insert(i, (key, previous_count + 1))
                pushed_forward = True
                break

        if not pushed_forward:
            self._sorted_freq_accesses.append((key, previous_count + 1))

        self.counts[key] = previous_count + 1

    def value(self, key):
        return self.counts.get(key, 0)
    
    # First - least frequently used
    def sorted_keys(self):
        yield from (key for key, _ in self._sorted_freq_accesses)
