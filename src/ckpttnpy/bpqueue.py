# -*- coding: utf-8 -*-
from .dllist import Dllink, Dllist

sentinel = Dllink([0, 8965])


class BPQueue:
    """bounded priority queue

    Bounded Priority Queue with integer keys in [a..b].
    Implemented by array (bucket) of doubly-linked lists.
    Efficient if key is bounded by a small integer value.

    Note that this class does not own the PQ nodes. This feature
    makes the nodes sharable between doubly linked list class and
    this class. In the FM algorithm, the node either attached to
    the gain buckets (PQ) or in the waitinglist (doubly linked list),
    but not in both of them in the same time.

    Another improvement is to make the array size one element bigger
    i.e. (b - a + 2). The extra dummy array element (which is called
    sentinel) is used to reduce the boundary checking during updating.

    All member functions assume that the keys are within the bound.
    """

    __slots__ = ("_max", "_offset", "_high", "_bucket")

    def __init__(self, a: int, b: int):
        """initialization

        Arguments:
            a (int):  lower bound
            b (int):  upper bound
        """
        assert a <= b
        self._max = 0
        self._offset = a - 1
        self._high = b - self._offset
        self._bucket = list(Dllist([0, 4848]) for _ in range(self._high + 1))
        self._bucket[0].append(sentinel)  # sentinel

    def set_key(self, it: Dllink, gain: int):
        """Set the key value

        Arguments:
            it (Dllink):  the item
            gain (int):  the key of it
        """
        it.data[0] = gain - self._offset

    def get_max(self) -> int:
        """Get the max value

        Returns:
            int:  maximum value
        """
        return self._max + self._offset

    def is_empty(self) -> bool:
        """whether empty

        Returns:
            bool:  description
        """
        return self._max == 0

    def clear(self):
        """reset the PQ"""
        while self._max > 0:
            self._bucket[self._max].clear()
            self._max -= 1

    def append_direct(self, it):
        """append item with internal key

        Arguments:
            it (Dllink):  the item
            k (int):  the key
        """
        assert it.data[0] > self._offset
        self.append(it, it.data[0])

    def append(self, it, k):
        """append item with external key

        Arguments:
            it (Dllink):  description
            k (int):  key
        """
        assert k > self._offset
        it.data[0] = k - self._offset
        if self._max < it.data[0]:
            self._max = it.data[0]
        self._bucket[it.data[0]].append(it)

    def appendfrom(self, nodes):
        """append from list

        Arguments:
            C (list):  description
        """
        for it in nodes:
            it.data[0] -= self._offset
            assert it.data[0] > 0
            self._bucket[it.data[0]].append(it)
        self._max = self._high
        while self._bucket[self._max].is_empty():
            self._max -= 1

    def popleft(self):
        """pop node with the highest key

        Returns:
            Dllink:  description
        """
        res = self._bucket[self._max].popleft()
        while self._bucket[self._max].is_empty():
            self._max -= 1
        return res.data

    def decrease_key(self, it, delta):
        """decrease key by delta

        Arguments:
            it (Dllink):  the item
            delta (int):  the change of the key

        Note that the order of items with same key will
        not be preserved.
        For FM algorithm, this is a prefered behavior.
        """
        # self._bucket[it.data[0]].detach(it)
        it.detach()
        it.data[0] += delta
        assert it.data[0] > 0
        assert it.data[0] <= self._high
        self._bucket[it.data[0]].append(it)  # FIFO
        if self._max < it.data[0]:
            self._max = it.data[0]
            return
        while self._bucket[self._max].is_empty():
            self._max -= 1

    def increase_key(self, it, delta):
        """increase key by delta

        Arguments:
            it (Dllink):  the item
            delta (int):  the change of the key

        Note that the order of items with same key will
        not be preserved.
        For FM algorithm, this is a prefered behavior.
        """
        # self._bucket[it.data[0]].detach(it)
        it.detach()
        it.data[0] += delta
        assert it.data[0] > 0
        assert it.data[0] <= self._high
        self._bucket[it.data[0]].appendleft(it)  # LIFO
        # self._bucket[it.data[0]].append(it)  # LIFO
        if self._max < it.data[0]:
            self._max = it.data[0]

    def modify_key(self, it, delta):
        """modify key by delta

        Arguments:
            it (Dllink):  the item
            delta (int):  the change of the key

        Note that the order of items with same key will
        not be preserved.
        For FM algorithm, this is a prefered behavior.
        """
        if it.next is None:  # locked
            return
        if delta > 0:
            self.increase_key(it, delta)
        elif delta < 0:
            self.decrease_key(it, delta)

    def detach(self, it):
        """detach the item from BPQueue

        Arguments:
            it (type):  the item
        """
        # self._bucket[it.data[0]].detach(it)
        it.detach()
        while self._bucket[self._max].is_empty():
            self._max -= 1

    # def __iter__(self):
    #     """iterator

    #     Returns:
    #         bpq_iterator
    #     """
    #     curkey = self._max
    #     while curkey > 0:
    #         for item in self._bucket[curkey]:
    #             yield item
    #         curkey -= 1

    def __iter__(self):
        """iterator

        Returns:
            bpq_iterator
        """
        return bpq_iterator(self)


class bpq_iterator:
    """bounded priority queue iterator

    Bounded Priority Queue Iterator. Traverse the queue in descending
    order. Detaching queue items may invalidate the iterator because
    the iterator makes a copy of current key.
    """

    def __init__(self, bpq):
        """[summary]

        Arguments:
            bpq (type):  description
        """
        self.bpq = bpq
        self.curkey = bpq._max
        self.curitem = iter(bpq._bucket[bpq._max])

    def __next__(self):
        """next

        Raises:
            StopIteration:  description

        Returns:
            Dllink:  description
        """
        while self.curkey > 0:
            try:
                res = next(self.curitem)
                return res
            except StopIteration:
                self.curkey -= 1
                self.curitem = iter(self.bpq._bucket[self.curkey])
        raise StopIteration

    # def __next__(self):
    #     """[summary]

    #     Returns:
    #         dtype:  description
    #     """
    #     return self.next()
