from typing import List


class SlNode:
    next: "SlNode"
    data: int

    def __init__(self, data: int):
        """initialization

        Keyword Arguments:
            data (type):  description
        """
        self.next = self
        self.data = data


class RobinIterator:
    __slots__ = ("cur", "stop")
    cur: SlNode
    stop: SlNode

    def __init__(self, node: SlNode) -> None:
        """[summary]

        Arguments:
            Robin (type):  description
        """
        self.cur = self.stop = node

    def __iter__(self) -> "RobinIterator":
        """iterable

        Returns:
            RobinIterator:  itself
        """
        return self

    def next(self):
        """next

        Raises:
            StopIteration:  description

        Returns:
            robinink:  description
        """
        self.cur = self.cur.next
        if self.cur != self.stop:
            return self.cur.data
        else:
            raise StopIteration()

    def __next__(self):
        """[summary]

        Returns:
            dtype:  description
        """
        return self.next()


class Robin:
    """Round Robin

    Raises:
        StopIteration:  description

    Returns:
        dtype:  description
    """

    __slots__ = "cycle"
    cycle: List[SlNode]

    def __init__(self, num_parts: int):
        self.cycle = list(SlNode(k) for k in range(num_parts))
        sl2 = self.cycle[-1]
        for sl1 in self.cycle:
            sl2.next = sl1
            sl2 = sl1

    def exclude(self, from_part: int):
        """iterator

        Returns:
            RobinIterator
        """
        return RobinIterator(self.cycle[from_part])


if __name__ == "__main__":
    r = Robin(5)
    for k in r.exclude(3):
        print(k)
