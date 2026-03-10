from components.utility.simple import SimpleUtility
from components.policy import Policy
from components.features.base import Feature
from components.ranking.base import Ranker


class DummyFeature(Feature):
    def on_access(self, key, timestamp, size: int = 0, latency: float = 0.0):
        pass
    
    def value(self, key):
        return 0.0

class DummyUtility(SimpleUtility):
    def compute(self, key, features, predictions=None, timestamp=None):
        return 0.0
    
class DummyRanker(Ranker):
    def select(self, utilities):
        return next(iter(utilities))

def Empty_Policy():
    feature = DummyFeature()
    return Policy(
        features=[feature], 
        utility_model=DummyUtility(feature),
        ranker=DummyRanker()
    )
