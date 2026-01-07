from components.policy import Policy
from components.core.storage import Storage

class Cache:
    def __init__(self, policy: Policy, storage: Storage):
        self.policy = policy
        self.storage = storage

    def access(self, key: int, timestamp: int, size: int) -> list[str]:
        actions = []
        hit = self.storage.contains(key)

        if hit:
            actions.append("hit")
        else:
            actions.append("miss")

        self.policy.on_access(key, timestamp)

        used_capacity = self.storage.used_capacity()
        if not hit:
            if used_capacity + size > self.storage.capacity:
                # Need to evict items
                actions.append("select-victims")

                victims = self.policy.select_victims(self.storage.keys())
                while used_capacity + size - sum([self.storage.data[v] for v in victims]) > self.storage.capacity:
                    # Continue selecting victims until enough space is freed
                    victims_left = [k for k in self.storage.keys() if k not in victims]
                    if not victims_left:
                        break

                    victims.extend(self.policy.select_victims(victims_left))

                if used_capacity + size - sum([self.storage.data[v] for v in victims]) <= self.storage.capacity:
                    # Has found enough space by evicting victims
                    for victim in victims:
                        actions.append(f"evict-{victim}")
                        self.storage.evict(victim)
                        self.policy.on_evict(victim)

            if not self.storage.is_full(size - 1):
                # If still not full, insert the new item
                actions.append(f"insert")
                self.storage.insert(key, size)
                self.policy.on_insert(key, timestamp)

        return actions
