class Node:
    __slots__ = ("key", "prev", "next")

    def __init__(self, key=None):
        self.key = key
        self.prev = None
        self.next = None

class DoublyLinkedList:
    """
        Doubly linked list for lower complexity cache ranking operations
    """
    __slots__ = ("head", "tail", "size")

    def __init__(self):
        self.head = Node(None)
        self.tail = Node(None)
        self.head.next = self.tail
        self.tail.prev = self.head
        self.size = 0

    def append(self, node: Node) -> None:
        last = self.tail.prev
        node.prev = last
        node.next = self.tail
        last.next = node
        self.tail.prev = node
        self.size += 1

    def remove(self, node: Node) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev
        node.prev = None
        node.next = None
        self.size -= 1

    def first_key(self):
        node = self.head.next
        return None if node is self.tail else node.key
