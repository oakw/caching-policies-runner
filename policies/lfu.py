from components.features.frequency import FrequencyFeature
from components.utility.simple import SimpleUtility
from components.ranking.lfu_ranker import LFURanker
from components.policy import Policy

def LFU():
    frequency = FrequencyFeature()
    utility = SimpleUtility(frequency)
    ranker = LFURanker()
    return Policy([frequency], utility, ranker)
