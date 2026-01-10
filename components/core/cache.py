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

                all_keys = self.storage.keys()
                victims = set(self.policy.select_victims(all_keys, timestamp=timestamp))
                while used_capacity + size - sum([self.storage.data[v] for v in victims]) > self.storage.capacity:
                    # Continue selecting victims until enough space is freed
                    if len(all_keys) == len(victims):
                        break

                    victims.update(self.policy.select_victims(all_keys - victims, timestamp=timestamp))

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
