# -*- coding: utf-8 -*-

class slnode:
    def __init__(self, data):
        """initialization

        Keyword Arguments:
            data (type):  description
        """
        self.next = self
        self.data = data


class robin:
    """Round Robin

    Raises:
        StopIteration:  description

    Returns:
        dtype:  description
    """

    __slots__ = ('cycle')

    def __init__(self, K: int):
        self.cycle = list(slnode(k) for k in range(K))
        sl2 = self.cycle[-1]
        for sl1 in self.cycle:
            sl2.next = sl1
            sl2 = sl1

    def exclude(self, fromPart: int):
        """iterator

        Returns:
            robin_iterator
        """
        return robin_iterator(self, fromPart)


class robin_iterator:
    __slots__ = ('cur', 'stop')

    def __init__(self, robin, fromPart: int):
        """[summary]

        Arguments:
            robin (type):  description
        """
        self.cur = self.stop = robin.cycle[fromPart]

    def __iter__(self):
        """iterable

        Returns:
            robin_iterator:  itself
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
    R = robin(5)
    for k in R.exclude(3):
        print(k)
