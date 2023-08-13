from typing import Iterable, List

from .dllist import Dllink, Dllist

Item = Dllink[List[int]]

sentinel = Item([0, 8965])


class BPQueue:
    """The `BPQueue` class is a bounded priority queue implementation using an array of doubly-linked
    lists, optimized for small integer keys.

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

    _max: int
    _offset: int
    _high: int
    _bucket: List[Dllist[List[int]]]

    def __init__(self, a: int, b: int) -> None:
        """
        The function initializes a BPQueue object with a lower bound and an upper bound.

        :param a: The lower bound of the range
        :type a: int
        :param b: The parameter `b` represents the upper bound of the range
        :type b: int

        Examples:
            >>> bpq = BPQueue(-3, 3)
            >>> bpq._bucket[0].is_empty()
            False
            >>> bpq._bucket[1].is_empty()
            True
        """
        assert a <= b
        self._max = 0
        self._offset = a - 1
        self._high = b - self._offset
        self._bucket = list(Dllist([i, 4848]) for i in range(self._high + 1))
        self._bucket[0].append(sentinel)  # sentinel

    def is_empty(self) -> bool:
        """
        The `is_empty` function checks if a BPQueue object is empty.
        :return: The method is returning a boolean value, indicating whether the object is empty or not.

        Examples:
            >>> bpq = BPQueue(-3, 3)
            >>> bpq.is_empty()
            True
        """
        return self._max == 0

    def get_max(self) -> int:
        """
        The `get_max` function returns the maximum value in a BPQueue object.
        :return: The method `get_max` returns the maximum value, which is an integer.

        Examples:
            >>> bpq = BPQueue(-3, 3)
            >>> bpq.get_max()
            -4
        """
        return self._max + self._offset

    def clear(self) -> None:
        """
        The `clear` function resets the priority queue by clearing all the buckets.

        Examples:
            >>> bpq = BPQueue(-3, 3)
            >>> bpq.clear()
            >>> bpq.is_empty()
            True
        """
        while self._max > 0:
            self._bucket[self._max].clear()
            self._max -= 1

    def set_key(self, it: Item, gain: int) -> None:
        """
        The function `set_key` sets the key value of an item by subtracting the offset from the given gain
        value.

        :param it: The `it` parameter is of type `Item` and represents the item for which the key value is being set
        :type it: Item
        :param gain: The `gain` parameter is an integer representing the key value that will be set for the item
        :type gain: int

        Examples:
            >>> bpq = BPQueue(-3, 3)
            >>> a = Dllink([0, 3])
            >>> bpq.set_key(a, 0)
            >>> a.data[0]
            4

        """
        it.data[0] = gain - self._offset

    def append_direct(self, it: Item) -> None:
        """
        The `append_direct` function appends an item to a list using its internal key.

        :param it: The parameter `it` is of type `Item`, which is a class or data structure representing an item
        :type it: Item

        Examples:
            >>> bpq = BPQueue(-3, 3)
            >>> a = Dllink([0, 3])
            >>> bpq.append_direct(a)
            >>> bpq.is_empty()
            False
        """
        assert it.data[0] > self._offset
        self.append(it, it.data[0])

    def append(self, it: Item, k: int) -> None:
        """
        The `append` function appends an item with an external key to a priority queue.

        :param it: The parameter "it" is of type Dllink, which is a class or object that represents a doubly linked list node. It is used to store the item that needs to be appended to the BPQueue
        :type it: Item
        :param k: The parameter `k` represents the external key that is associated with the item being appended to the BPQueue
        :type k: int

        Examples:
            >>> bpq = BPQueue(-3, 3)
            >>> a = Dllink([0, 3])
            >>> bpq.append(a, 0)
            >>> bpq.is_empty()
            False
            >>> a.data[0]
            4
        """
        assert k > self._offset
        it.data[0] = k - self._offset
        if self._max < it.data[0]:
            self._max = it.data[0]
        self._bucket[it.data[0]].append(it)

    def appendfrom(self, nodes: Iterable[Item]) -> None:
        """
        The `appendfrom` function appends items from a list to a bucket, adjusting the data values of the
        items and updating the maximum value.

        :param nodes: The `nodes` parameter is an iterable of `Item` objects
        :type nodes: Iterable[Item]

        Examples:
            >>> bpq = BPQueue(-3, 3)
            >>> a = Dllink([0, 3])
            >>> b = Dllink([1, 2])
            >>> bpq.appendfrom([a, b])
            >>> bpq.is_empty()
            False

        """
        for it in nodes:
            it.data[0] -= self._offset
            assert it.data[0] > 0
            self._bucket[it.data[0]].append(it)
        self._max = self._high
        while self._bucket[self._max].is_empty():
            self._max -= 1

    def popleft(self) -> Item:
        """
        The `popleft` function removes and returns the node with the highest key from the BPQueue.
        :return: The method `popleft` returns a `Dllink` object.

        Examples:
            >>> bpq = BPQueue(-3, 3)
            >>> a = Dllink([0, 3])
            >>> bpq.append(a, 0)
            >>> b = bpq.popleft()
            >>> bpq.is_empty()
            True
        """
        res = self._bucket[self._max].popleft()
        while self._bucket[self._max].is_empty():
            self._max -= 1
        return res

    def decrease_key(self, it: Item, delta: int) -> None:
        """
        The `decrease_key` function decreases the key of an item by a specified delta and updates the item's
        position in a bucket data structure.

        :param it: it is a reference to an item in a doubly linked list
        :type it: Item
        :param delta: The parameter "delta" represents the change in the key value of the item. It is an integer value that determines how much the key value should be decreased
        :type delta: int
        :return: There is no return statement in the code, so nothing is being returned.

        Note:
            The order of items with same key will not be preserved. For FM algorithm, this is a prefered behavior.

        Examples:
            >>> bpq = BPQueue(-3, 3)
            >>> a = Dllink([0, 3])
            >>> bpq.append(a, 0)
            >>> bpq.decrease_key(a, 1)
            >>> a.data[0]
            3
        """
        it.detach()
        it.data[0] -= delta
        assert it.data[0] > 0
        assert it.data[0] <= self._high
        self._bucket[it.data[0]].append(it)  # FIFO
        if self._max < it.data[0]:
            self._max = it.data[0]
            return
        while self._bucket[self._max].is_empty():
            self._max -= 1

    def increase_key(self, it: Item, delta: int) -> None:
        """
        The `increase_key` function increases the key of an item by a given delta and updates the item's
        position in a bucket list.

        :param it: it is a variable of type Item, which represents an item in a data structure
        :type it: Item
        :param delta: The `delta` parameter in the `increase_key` function represents the change in the key
        value of the item `it`. It is an integer value that determines how much the key value should be
        increased
        :type delta: int

        Note:
            The order of items with same key will not be preserved. For FM algorithm, this is a prefered behavior.

        Examples:
            >>> bpq = BPQueue(-3, 3)
            >>> a = Dllink([0, 3])
            >>> bpq.append(a, 0)
            >>> bpq.increase_key(a, 1)
            >>> a.data[0]
            5
        """
        it.detach()
        it.data[0] += delta
        assert it.data[0] > 0
        assert it.data[0] <= self._high
        self._bucket[it.data[0]].appendleft(it)  # LIFO
        # self._bucket[it.data[0]].append(it)  # LIFO
        if self._max < it.data[0]:
            self._max = it.data[0]

    def modify_key(self, it: Item, delta: int) -> None:
        """
        The `modify_key` function modifies the key of an item by a specified delta and updates the item's
        position in a bucket data structure.

        :param it: it is a reference to an item in a doubly linked list
        :type it: Item
        :param delta: The parameter "delta" represents the change in the key value of the item. It is an
        integer value that determines how much the key value should be modified
        :type delta: int
        :return: There is no return statement in the code, so nothing is being returned.

        Note:
            The order of items with same key will not be preserved. For FM algorithm, this is a prefered behavior.

        Examples:
            >>> bpq = BPQueue(-3, 3)
            >>> a = Dllink([0, 3])
            >>> bpq.append(a, 0)
            >>> bpq.modify_key(a, 1)
            >>> a.data[0]
            5

        """
        if it.next == it:  # locked
            return
        if delta > 0:
            self.increase_key(it, delta)
        elif delta < 0:
            self.decrease_key(it, -delta)

    def detach(self, it: Item) -> None:
        """
        The `detach` function detachs an item from a priority queue.

        :param it: The parameter "it" is of type Dllink, which is a class or object that represents a doubly
        linked list node to be detached from the BPQueue
        :type it: Item

        Examples:
            >>> bpq = BPQueue(-3, 3)
            >>> a = Dllink([0, 3])
            >>> bpq.append(a, 0)
            >>> bpq.detach(a)
            >>> bpq.is_empty()
            True
        """
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
        """
        The function returns an iterator object for a priority queue.
        :return: The `__iter__` method is returning an instance of the `BPQueueIterator` class.
        """
        return BPQueueIterator(self)


class BPQueueIterator:
    """The BPQueueIterator class is a bounded priority queue iterator that allows traversal of the queue in descending order.

    Bounded Priority Queue Iterator. Traverse the queue in descending
    order. Detaching queue items may invalidate the iterator because
    the iterator makes a copy of current key.
    """

    def __init__(self, bpq: BPQueue) -> None:
        """
        The function initializes an object with a given BPQueue and sets the current key and item.

        :param bpq: The `bpq` parameter is of type `BPQueue`. It is an object that represents a bounded priority queue
        :type bpq: BPQueue

        Examples:
            >>> bpq = BPQueue(-3, 3)
            >>> a = Dllink([0, 3])
            >>> bpq.append(a, 0)
            >>> it = BPQueueIterator(bpq)
            >>> b = next(it)
            >>> next(it)
            Traceback (most recent call last):
            ...
            StopIteration
        """
        self.bpq = bpq
        self.curkey = bpq._max
        self.curitem = iter(bpq._bucket[bpq._max])

    def __next__(self) -> Item:
        """
        The `__next__` function returns the next item in a linked list, iterating through the buckets in
        reverse order.
        :return: an object of type "Dllink".

        Examples:
            >>> bpq = BPQueue(-3, 3)
            >>> a = Dllink([0, 3])
            >>> bpq.append(a, 0)
            >>> it = BPQueueIterator(bpq)
            >>> b = next(it)
            >>> next(it)
            Traceback (most recent call last):
            ...
            StopIteration

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
