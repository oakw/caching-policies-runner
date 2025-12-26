from components.policy import Policy
from components.core.storage import Storage

class Cache:
    def __init__(self, policy: Policy, storage: Storage):
        self.policy = policy
        self.storage = storage

    def access(self, key: int, timestamp: int) -> bool:
        hit = self.storage.contains(key)

        self.policy.on_access(key, timestamp)

        if not hit:
            if self.storage.is_full():
                victim = self.policy.select_victim(self.storage.keys())
                self.storage.evict(victim)
                self.policy.on_evict(victim)

            self.storage.insert(key)
            self.policy.on_insert(key, timestamp)

        return hit
