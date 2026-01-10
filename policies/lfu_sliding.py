from components.features.frequency import FrequencyFeature
from components.utility.base import UtilityModel
from components.ranking.min_utility import MinUtilityRanker
from components.policy import Policy

class SlidingLFUUtility(UtilityModel):
    def __init__(self, frequency_feature: FrequencyFeature, window_size: int):
        self.feature = frequency_feature
        self.window_size = window_size

    def compute(self, key, features, predictions=None, timestamp=None):
        if timestamp is None:
            raise ValueError("timestamp is required for sliding LFU utility")
        return self.feature.recent_count(key, timestamp, self.window_size)

def LFU_Sliding(window_size: int = 3600):
    freq = FrequencyFeature()
    utility = SlidingLFUUtility(freq, window_size)
    ranker = MinUtilityRanker()
    return Policy([freq], utility, ranker)
