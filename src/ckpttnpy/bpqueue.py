# -*- coding: utf-8 -*-
from .dllist import dllink

sentinel = dllink(8965)


class bpqueue:
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

    All the member functions assume that the keys are within the bound.
    """

    __slots__ = ('max', 'offset', 'high', 'bucket')

    def __init__(self, a: int, b: int):
        """initialization

        Arguments:
            a (int):  lower bound
            b (int):  upper bound
        """
        self.max = 0

        assert a <= b
        self.offset = a - 1
        self.high = b - self.offset
        self.bucket = list(dllink(4848) for _ in range(self.high + 1))
        self.bucket[0].append(sentinel)  # sentinel

    def set_key(self, it: dllink, gain: int):
        """Set the key value

        Arguments:
            it (dllink):  the item
            gain (int):  the key of it
        """
        it.key = gain - self.offset

    def get_max(self) -> int:
        """Get the max value

        Returns:
            int:  maximum value
        """
        return self.max + self.offset

    def is_empty(self) -> bool:
        """whether empty

        Returns:
            bool:  description
        """
        return self.max == 0

    def clear(self):
        """reset the PQ """
        while self.max > 0:
            self.bucket[self.max].clear()
            self.max -= 1

    def append_direct(self, it):
        """append item with internal key

        Arguments:
            it (dllink):  the item
            k (int):  the key
        """
        assert it.key > self.offset
        self.append(it, it.key)

    def append(self, it, k):
        """append item with external key

        Arguments:
            it (dllink):  description
            k (int):  key
        """
        assert k > self.offset
        it.key = k - self.offset
        if self.max < it.key:
            self.max = it.key
        self.bucket[it.key].append(it)

    def appendfrom(self, nodes):
        """append from list

        Arguments:
            C (list):  description
        """
        for it in nodes:
            it.key -= self.offset
            assert it.key > 0
            self.bucket[it.key].append(it)
        self.max = self.high
        while self.bucket[self.max].is_empty():
            self.max -= 1

    def popleft(self):
        """pop node with the highest key

        Returns:
            dllink:  description
        """
        res = self.bucket[self.max].popleft()
        while self.bucket[self.max].is_empty():
            self.max -= 1
        return res

    def decrease_key(self, it, delta):
        """decrease key by delta

        Arguments:
            it (dllink):  the item
            delta (int):  the change of the key

        Note that the order of items with same key will
        not be preserved.
        For FM algorithm, this is a prefered behavior.
        """
        # self.bucket[it.key].detach(it)
        it.detach()
        it.key += delta
        assert it.key > 0
        assert it.key <= self.high
        self.bucket[it.key].append(it)  # FIFO
        if self.max < it.key:
            self.max = it.key
            return
        while self.bucket[self.max].is_empty():
            self.max -= 1

    def increase_key(self, it, delta):
        """increase key by delta

        Arguments:
            it (dllink):  the item
            delta (int):  the change of the key

        Note that the order of items with same key will
        not be preserved.
        For FM algorithm, this is a prefered behavior.
        """
        # self.bucket[it.key].detach(it)
        it.detach()
        it.key += delta
        assert it.key > 0
        assert it.key <= self.high
        self.bucket[it.key].appendleft(it)  # LIFO
        # self.bucket[it.key].append(it)  # LIFO
        if self.max < it.key:
            self.max = it.key

    def modify_key(self, it, delta):
        """modify key by delta

        Arguments:
            it (dllink):  the item
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
        """detach the item from bpqueue

        Arguments:
            it (type):  the item
        """
        # self.bucket[it.key].detach(it)
        it.detach()
        while self.bucket[self.max].is_empty():
            self.max -= 1

    def __iter__(self):
        """iterator

        Returns:
            bpq_iterator
        """
        # return bpq_iterator(self)
        curkey = self.max
        while curkey > 0:
            for item in self.bucket[curkey]:
                yield item
            curkey -= 1


# class bpq_iterator:
#     """bounded priority queue iterator

#     Bounded Priority Queue Iterator. Traverse the queue in descending
#     order. Detaching queue items may invalidate the iterator because
#     the iterator makes a copy of current key.
#     """

#     def __init__(self, bpq):
#         """[summary]

#         Arguments:
#             bpq (type):  description
#         """
#         self.bpq = bpq
#         self.curkey = bpq.max
#         self.curitem = iter(bpq.bucket[bpq.max])

#     def next(self):
#         """next

#         Raises:
#             StopIteration:  description

#         Returns:
#             dllink:  description
#         """
#         while self.curkey > 0:
#             try:
#                 res = next(self.curitem)
#                 return res
#             except StopIteration:
#                 self.curkey -= 1
#                 self.curitem = iter(self.bpq.bucket[self.curkey])
#         raise StopIteration

#     def __next__(self):
#         """[summary]

#         Returns:
#             dtype:  description
#         """
#         return self.next()
