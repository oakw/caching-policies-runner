from .base import Ranker
from ._linked import Node, DoublyLinkedList

class LRURanker(Ranker):
    """
        Ranks candidates by recency of access,
        evicting the least recently used item among the candidates
    """
    def __init__(self):
        self._nodes = {}
        self._list = DoublyLinkedList()

    def on_access(self, key, timestamp, size: int = 0, latency: float = 0.0):
        node = self._nodes.get(key)
        if node is None:
            return
        self._list.remove(node)
        self._list.append(node)

    def on_insert(self, key, timestamp):
        node = self._nodes.get(key)
        if node is not None:
            self._list.remove(node)
            self._list.append(node)
            return
        node = Node(key)
        self._nodes[key] = node
        self._list.append(node)

    def on_evict(self, key):
        node = self._nodes.pop(key, None)
        if node is None:
            return
        self._list.remove(node)

    def select(self, utilities):
        candidates = set(utilities)
        node = self._list.head.next
        # Since the list maintains global order, we can simply return the first candidate we find in the list, which will be the LRU among them
        while node is not self._list.tail:
            if node.key in candidates:
                return node.key
            node = node.next

        return min(candidates, key=lambda k: utilities[k])
