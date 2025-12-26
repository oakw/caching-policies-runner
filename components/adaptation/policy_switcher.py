from .base import Adapter

class PolicySwitcher(Adapter):
    def __init__(self, policies):
        self.policies = policies
        self.active = policies[0]

    def observe(self, outcome):
        pass

    def update(self):
        pass
