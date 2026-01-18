from components.features.frequency import FrequencyFeature
from components.utility.base import UtilityModel
from components.ranking.min_utility import MinUtilityRanker
from components.policy import Policy

# Frequency decays when an item is not accessed,
# so apply penalty based on time since last access.
class DecayedLFUUtility(UtilityModel):
    def __init__(self, frequency_feature: FrequencyFeature, tau: float):
        self.feature = frequency_feature
        self.tau = float(tau)

    def compute(self, key, features, predictions=None, timestamp=None):
        if timestamp is None:
            raise ValueError("timestamp required for decayed LFU utility")
        return self.feature.decayed_frequency(key, timestamp, self.tau)

def LFU_Aging(tau: float = 3600.0):
    freq = FrequencyFeature()
    utility = DecayedLFUUtility(freq, tau)
    ranker = MinUtilityRanker()
    return Policy([freq], utility, ranker)
