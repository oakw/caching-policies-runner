class Policy:
    def __init__(self, features, utility_model, ranker):
        self.features = features
        self.utility_model = utility_model
        self.ranker = ranker

    def on_access(self, key, timestamp):
        for f in self.features:
            f.on_access(key, timestamp)

    def on_insert(self, key, timestamp):
        pass

    def on_evict(self, key):
        pass

    def select_victims(self, keys):
        if len(keys) == 0:
            return []
            
        utilities = {
            key: self.utility_model.compute(key, self.features)
            for key in keys
        }

        return [self.ranker.select(utilities)]
