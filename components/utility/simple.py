from .base import UtilityModel

class SimpleUtility(UtilityModel):
    def __init__(self, feature):
        self.feature = feature

    def compute(self, key, features, predictions=None, timestamp=None):
        return self.feature.value(key)    
