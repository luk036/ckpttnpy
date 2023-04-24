from typing import Generic, TypeVar

T = TypeVar("T")


class SlNode(Generic[T]):
    next: "SlNode[T]"
    data: T

    def __init__(self, data: T) -> None:
        """initialization

        Keyword Arguments:
            data (type):  description
        """
        self.next = self
        self.data = data


class Robin:
    """Round Robin

    Raises:
        StopIteration:  description

    Returns:
        dtype:  description
    """

    __slots__ = "cycle"

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
        return RobinIterator(self, from_part)


class RobinIterator:
    __slots__ = ("cur", "stop")

    def __init__(self, Robin, from_part: int):
        """[summary]

        Arguments:
            Robin (type):  description
        """
        self.cur = self.stop = Robin.cycle[from_part]

    def __iter__(self):
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
            raise StopIteration

    def __next__(self):
        """[summary]

        Returns:
            dtype:  description
        """
        return self.next()


if __name__ == "__main__":
    r = Robin(5)
    for k in r.exclude(3):
        print(k)
