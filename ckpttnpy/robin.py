from .dllist import dllink


class robin:
    """Round Robin

    Raises:
        StopIteration -- [description]

    Returns:
        [type] -- [description]
    """

    def __init__(self, K):
        self.cycle = list(dllink(k) for k in range(K))
        for k in range(K - 1):
            self.cycle[k].next = self.cycle[k+1]
        self.cycle[K - 1].next = self.cycle[0]

    def exclude(self, fromPart):
        """iterator

        Returns:
            robin_iterator
        """
        return robin_iterator(self, fromPart)


class robin_iterator:
    def __init__(self, robin, fromPart):
        """[summary]

        Arguments:
            robin {[type]} -- [description]
        """
        self.cur = self.stop = robin.cycle[fromPart]

    def __iter__(self):
        """iterable

        Returns:
            robin_iterator -- itself
        """
        return self

    def next(self):
        """next

        Raises:
            StopIteration -- [description]

        Returns:
            robinink -- [description]
        """
        self.cur = self.cur.next
        if self.cur != self.stop:
            return self.cur.idx
        else:
            raise StopIteration

    def __next__(self):
        """[summary]

        Returns:
            [type] -- [description]
        """
        return self.next()


if __name__ == "__main__":
    R = robin(5)
    for k in R.exclude(3):
        print(k)
