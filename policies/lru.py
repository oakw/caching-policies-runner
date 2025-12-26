from components.features.recency import RecencyFeature
from components.utility.simple import SimpleUtility
from components.ranking.min_utility import MinUtilityRanker
from components.policy import Policy

def LRU():
    recency = RecencyFeature()
    utility = SimpleUtility(recency)
    ranker = MinUtilityRanker()
    return Policy([recency], utility, ranker)
