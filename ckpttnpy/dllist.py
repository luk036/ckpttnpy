class dllink:
    """doubly linked list/node

    Generic Node. For efficiency, the objects of this class can be
    attached to bpqueue (bounded priority queue) and dllink (list). 
    In the FM algorithm, a node is either attached to a gain bucket
    or waitinglist.
    """

    def __init__(self, idx=None, key=0):
        """initialization

        Keyword Arguments:
            idx {[type]} -- [description] (default: {None})
            key {int} -- [description] (default: {0})
        """
        self.next = self.prev = self
        self.idx = idx
        self.key = key

    def detach(self):
        """detach"""
        assert self.next is not None
        n = self.next
        p = self.prev
        p.next = n
        n.prev = p

    def lock(self):
        self.next = None

    def is_locked(self):
        return self.next is None

    def __bool__(self):
        return self.next != self

    def is_empty(self):
        """is_empty

        Returns:
            bool -- [description]
        """
        return self.next == self

    def clear(self):
        """clear"""
        self.next = self.prev = self

    def appendleft(self, node):
        """append left

        Arguments:
            node {dllink} -- [description]
        """
        node.next = self.next
        self.next.prev = node
        self.next = node
        node.prev = self

    def append(self, node):
        """append

        Arguments:
            node {dllink} -- [description]
        """
        node.prev = self.prev
        self.prev.next = node
        self.prev = node
        node.next = self

    def popleft(self):
        """pop left

        Returns:
            dllink -- [description]
        """
        res = self.next
        self.next = res.next
        self.next.prev = self
        return res

    def pop(self):
        """pop

        Returns:
            dllink -- [description]
        """
        res = self.prev
        self.prev = res.prev
        self.prev.next = self
        return res

    def __iter__(self):
        """iterable

        Returns:
            dllink -- itself
        """
        return dll_iterator(self)


class dll_iterator:
    def __init__(self, link):
        """[summary]

        Arguments:
            link {[type]} -- [description]
        """
        self.link = link
        self.cur = link.next

    def next(self):
        """next

        Raises:
            StopIteration -- [description]

        Returns:
            dllink -- [description]
        """
        if self.cur != self.link:
            res = self.cur
            self.cur = self.cur.next
            return res
        else:
            raise StopIteration

    def __next__(self):
        """[summary]

        Returns:
            [type] -- [description]
        """
        return self.next()
