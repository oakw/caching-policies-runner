from components.features.recency import RecencyFeature
from components.utility.simple import SimpleUtility
from components.ranking.lru_ranker import LRURanker
from components.policy import Policy

def LRU():
    recency = RecencyFeature()
    utility = SimpleUtility(recency)
    ranker = LRURanker()
    return Policy([recency], utility, ranker)
