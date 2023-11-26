from typing import List


class SlNode:
    """Node for a Singly-linked list
    The `SlNode` class represents a node in a singly-linked list, with a `next` pointer and a `data`
    value.
    """

    next: "SlNode"
    data: int

    def __init__(self, data: int):
        """
        The function initializes an object with a data attribute and a next attribute that points to itself.

        :param data: The `data` parameter is an integer that represents the value to be stored in the node
        :type data: int
        """
        self.next = self
        self.data = data


class RobinIterator:
    """The `RobinIterator` class is an iterator that iterates over a singly linked list starting from a
    given node.
    """

    __slots__ = ("cur", "stop")
    cur: SlNode
    stop: SlNode

    def __init__(self, node: SlNode) -> None:
        """
        The function initializes the current and stop pointers to the given node.

        :param node: The `node` parameter is an instance of the `SlNode` class. It represents a node in a
        singly linked list
        :type node: SlNode

        Examples:
            >>> node = SlNode(1)
            >>> iter = RobinIterator(node)
            >>> iter.cur == node
            True
            >>> iter.stop == node
            True
            >>> iter.cur.next == node
            True
            >>> iter.stop.next == node
            True
            >>> iter.cur.data == 1
            True
            >>> iter.stop.data == 1
            True
            >>> iter.cur.next.data == 1
            True
            >>> iter.stop.next.data == 1
            True
            >>> iter.cur.next.next == node
            True
            >>> iter.stop.next.next == node
            True
            >>> iter.cur.next.next.data == 1
            True
            >>> iter.stop.next.next.data == 1
            True
            >>> iter.cur.next.next.next == node
            True
            >>> iter.stop.next.next.next == node
            True
            >>> iter.cur.next.next.next.data == 1
            True
            >>> iter.stop.next.next.next.data == 1
            True
            >>> iter.cur.next.next.next.next == node
            True
        """
        self.cur = self.stop = node

    def __iter__(self) -> "RobinIterator":
        """
        The function returns an instance of the RobinIterator class.
        :return: The `__iter__` method is returning an instance of the `RobinIterator` class.
        """
        return self

    def next(self) -> int:
        """
        The `next` function returns the next element in a linked list and raises a `StopIteration` exception
        if there are no more elements.
        :return: The method is returning an integer value.
        """
        self.cur = self.cur.next
        if self.cur != self.stop:
            return self.cur.data
        else:
            raise StopIteration()

    def __next__(self):
        """
        The __next__ function returns the next item in the iterator.
        :return: The `next()` method is being called and its return value is being returned.
        """
        return self.next()


class Robin:
    """Round Robin
    The `Robin` class implements a round-robin algorithm for cycling through a list of parts, and the
    `exclude` method returns an iterator starting from a specified part.
    The `Robin` class implements a round-robin algorithm for cycling through a list of parts, and the
    `exclude` method returns an iterator starting from a specified part.
    """

    __slots__ = "cycle"
    cycle: List[SlNode]

    def __init__(self, num_parts: int):
        """
        The function initializes a cycle of linked nodes with a given number of parts.

        :param num_parts: The `num_parts` parameter is an integer that represents the number of parts in the
        cycle
        :type num_parts: int
        """
        self.cycle = list(SlNode(k) for k in range(num_parts))
        sl2 = self.cycle[-1]
        for sl1 in self.cycle:
            sl2.next = sl1
            sl2 = sl1

    def exclude(self, from_part: int) -> RobinIterator:
        """
        The `exclude` function returns a `RobinIterator` object that excludes a specified part of a cycle.

        :param from_part: The `from_part` parameter is an integer that represents the starting index of the
        cycle that should be excluded
        :type from_part: int
        :return: The `exclude` method is returning a `RobinIterator` object.

        Examples:
            >>> r = Robin(5)
            >>> iter = r.exclude(3)
            >>> iter.cur.data == 3
            True
            >>> iter.stop.data == 3
            True
        """
        return RobinIterator(self.cycle[from_part])


if __name__ == "__main__":
    r = Robin(5)
    for k in r.exclude(3):
        print(k)
