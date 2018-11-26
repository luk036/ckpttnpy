class dllink:
    """doubly linked list

    Raises:
        StopIteration -- [description]

    Returns:
        [type] -- [description]
    """

    def __init__(self, idx=None, key=0):
        """initialization

        Keyword Arguments:
            idx {[type]} -- [description] (default: {None})
            key {int} -- [description] (default: {0})
        """
        self.idx = idx
        self.key = key
        self.next = self.prev = self

    def detach(self):
        """detach"""
        n = self.next
        p = self.prev
        p.next = n
        n.prev = p

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
