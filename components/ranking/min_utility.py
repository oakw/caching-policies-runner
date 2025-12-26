from .base import Ranker

class MinUtilityRanker(Ranker):
    def select(self, utilities):
        return min(utilities, key=utilities.get)
