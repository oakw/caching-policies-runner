from .base import UtilityModel

class SimpleUtility(UtilityModel):
    def __init__(self, feature):
        self.feature = feature

    def compute(self, key, features, predictions=None):
        return self.feature.value(key)

    def lowest_utility_accessible(self):
        """ Shows that can cut shortcut without evaluating all keys """
        return hasattr(self.feature, "sorted_keys")
    
    def next_lowest_utility_key(self):
        """ Yields keys in the specified order """
        if not self.lowest_utility_accessible():
            raise NotImplementedError("Feature does not support sorted keys, check by lowest_utility_accessible() first.")

        for key in self.feature.sorted_keys():
            yield key
