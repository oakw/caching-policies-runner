from components.policy import Policy
from components.core.storage import Storage

class Cache:
    def __init__(self, policy: Policy, storage: Storage):
        self.policy = policy
        self.storage = storage

    def access(self, key: int, timestamp: int, size: int) -> bool:
        hit = self.storage.contains(key)

        self.policy.on_access(key, timestamp)

        if not hit:
            if self.storage.is_full(size):
                victims = self.policy.select_victims(self.storage.keys())
                for victim in victims:
                    self.storage.evict(victim)
                    self.policy.on_evict(victim)

            if   not self.storage.is_full(size):
                self.storage.insert(key, size)
                self.policy.on_insert(key, timestamp)

        return hit
