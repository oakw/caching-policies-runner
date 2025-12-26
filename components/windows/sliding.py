from .base import Window

class SlidingWindow(Window):
    def __init__(self, size):
        self.size = size

    def update(self, event):
        pass

    def project(self, raw_features):
        return raw_features
