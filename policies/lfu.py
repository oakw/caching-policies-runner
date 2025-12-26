from components.features.frequency import FrequencyFeature
from components.utility.simple import SimpleUtility
from components.ranking.min_utility import MinUtilityRanker
from components.policy import Policy

def LFU():
    frequency = FrequencyFeature()
    utility = SimpleUtility(frequency)
    ranker = MinUtilityRanker()
    return Policy([frequency], utility, ranker)
