from .dllist import dllink


class bpqueue:
    """bounded priority queue

    Raises:
        StopIteration -- [description]

    Returns:
        [type] -- [description]
    """

    def __init__(self, a, b):
        """initialization

        Arguments:
            a {int} -- lower bound
            b {int} -- upper bound
        """
        self.offset = a - 1
        self.high = b - self.offset
        self.max = 0
        self.sentinel = dllink(8965)
        self.bucket = list(dllink(4848) for _ in range(self.high + 1))
        self.bucket[0].append(self.sentinel)  # sentinel

    def get_key(self, it):
        """Get the key value

        Arguments:
            it {dllink} -- [description]

        Returns:
            int -- key
        """
        return it.key + self.offset

    def set_key(self, it, gain):
        """Get the key value

        Arguments:
            it {dllink} -- [description]

        Returns:
            int -- key
        """
        it.key = gain - self.offset

    def get_max(self):
        """Get the max value

        Returns:
            int -- maximum value
        """
        return self.max + self.offset

    def is_empty(self):
        """is_empty

        Returns:
            bool -- [description]
        """
        return self.max == 0

    def clear(self):
        """clear"""
        while self.max > 0:
            self.bucket[self.max].clear()
            self.max -= 1

    def append(self, it, k):
        """append

        Arguments:
            it {dllink} -- [description]
            k {int} -- key
        """
        key = k - self.offset
        if self.max < key:
            self.max = key
        it.key = key
        self.bucket[key].append(it)

    def appendfrom(self, C):
        """append from list

        Arguments:
            C {list} -- [description]
        """
        for it in C:
            it.key -= self.offset
            self.bucket[it.key].append(it)
        self.max = self.high
        while self.bucket[self.max].is_empty():
            self.max -= 1

    def popleft(self):
        """pop node with maximum key

        Returns:
            dllink -- [description]
        """
        res = self.bucket[self.max].popleft()
        while self.bucket[self.max].is_empty():
            self.max -= 1
        return res

    def decrease_key(self, it, delta):
        """decrease key

        Arguments:
            it {dllink} -- [description]
            delta {int} -- [description]
        """
        # self.bucket[it.key].detach(it)
        it.detach()
        it.key += delta
        assert it.key > 0
        assert it.key <= self.high
        self.bucket[it.key].append(it)  # FIFO
        while self.bucket[self.max].is_empty():
            self.max -= 1

    def increase_key(self, it, delta):
        """increase key

        Arguments:
            it {dllink} -- [description]
            delta {int} -- [description]
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
        """modify key

        Arguments:
            it {dllink} -- [description]
            delta {int} -- [description]
        """
        if delta > 0:
            self.increase_key(it, delta)
        elif delta < 0:
            self.decrease_key(it, delta)

    # def detach(self, it):
    #     """detach a node from bpqueue

    #     Arguments:
    #         it {[type]} -- [description]
    #     """
    #     # self.bucket[it.key].detach(it)
    #     it.detach()
    #     while self.bucket[self.max].is_empty():
    #         self.max -= 1

    def __iter__(self):
        """iterator

        Returns:
            bpq_iterator
        """
        return bpq_iterator(self)


class bpq_iterator:
    def __init__(self, bpq):
        """[summary]
        
        Arguments:
            bpq {[type]} -- [description]
        """
        self.bpq = bpq
        self.curkey = bpq.max
        self.curitem = iter(bpq.bucket[bpq.max])

    def next(self):
        """next

        Raises:
            StopIteration -- [description]

        Returns:
            dllink -- [description]
        """
        while self.curkey > 0:
            try:
                res = next(self.curitem)
                return res
            except StopIteration:
                self.curkey -= 1
                self.curitem = iter(self.bpq.bucket[self.curkey])
        raise StopIteration

    def __next__(self):
        """[summary]
        
        Returns:
            [type] -- [description]
        """
        return self.next()
