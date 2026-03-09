from .base import Ranker
from ._linked import Node, DoublyLinkedList

class LRURanker(Ranker):
    def __init__(self):
        self._nodes = {}
        self._list = DoublyLinkedList()

    def on_access(self, key, timestamp, size: int = 0, latency: float = 0.0):
        node = self._nodes.get(key)
        if node is None:
            node = Node(key)
            self._nodes[key] = node
            self._list.append(node)
            return
        self._list.remove(node)
        self._list.append(node)

    def on_insert(self, key, timestamp):
        self.on_access(key, timestamp)

    def on_evict(self, key):
        node = self._nodes.pop(key, None)
        if node is None:
            return
        self._list.remove(node)

    def select(self, utilities):
        k = self._list.first_key()
        return k if k is not None else min(utilities, key=utilities.get)
