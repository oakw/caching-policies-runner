from .base import Ranker
from ._linked import Node, DoublyLinkedList

class _LFUNode(Node):
    __slots__ = ("freq",)

    def __init__(self, key, freq: int):
        super().__init__(key)
        self.freq = freq

class LFURanker(Ranker):
    def __init__(self):
        self._nodes = {}
        self._lists = {}
        self._min = 0

    def _list(self, freq: int) -> DoublyLinkedList:
        lst = self._lists.get(freq)
        if lst is None:
            lst = DoublyLinkedList()
            self._lists[freq] = lst
        return lst

    def on_access(self, key, timestamp, size: int = 0, latency: float = 0.0):
        node = self._nodes.get(key)
        if node is None:
            node = _LFUNode(key, 1)
            self._nodes[key] = node
            self._list(1).append(node)
            self._min = 1
            return

        old = node.freq
        old_list = self._lists[old]
        old_list.remove(node)
        if old_list.size == 0:
            self._lists.pop(old, None)
            if self._min == old:
                self._min = old + 1

        node.freq = old + 1
        self._list(node.freq).append(node)

    def on_insert(self, key, timestamp):
        self.on_access(key, timestamp)

    def on_evict(self, key):
        node = self._nodes.pop(key, None)
        if node is None:
            return
        lst = self._lists.get(node.freq)
        if lst is not None:
            lst.remove(node)
            if lst.size == 0:
                self._lists.pop(node.freq, None)
                if self._min == node.freq:
                    self._min = 0

    def select(self, utilities):
        if not self._nodes:
            return min(utilities, key=utilities.get)

        lst = self._lists.get(self._min)
        if lst is None or lst.size == 0:
            if not self._lists:
                return min(utilities, key=utilities.get)
            self._min = min(self._lists)
            lst = self._lists[self._min]

        k = lst.first_key()
        return k if (k is not None and k in utilities) else min(utilities, key=utilities.get)
