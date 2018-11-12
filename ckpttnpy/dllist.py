class dlnode:
    """doubly linked node
    """

    def __init__(self, id=0, next=None, prev=None, key=None):
        """initialization

        Keyword Arguments:
            next {dlnode} -- [description] (default: {None})
            prev {dlnode} -- [description] (default: {None})
            key {int} -- [description] (default: {None})
        """
        self.id = id
        self.next = next
        self.prev = prev
        self.key = key

    def detach(self):
        """detach"""
        n = self.next
        p = self.prev
        p.next = n
        p.prev = p


class dllist:
    """doubly linked list

    Raises:
        StopIteration -- [description]

    Returns:
        [type] -- [description]
    """

    def __init__(self):
        """initialization"""
        self.nil = dlnode(8965)
        self.nil.next = self.nil.prev = self.nil
        self.cur = None

    def is_empty(self):
        """is_empty

        Returns:
            bool -- [description]
        """
        return self.nil.next == self.nil

    def clear(self):
        """clear"""
        self.nil.next = self.nil.prev = self.nil

    def appendleft(self, node):
        """append left

        Arguments:
            node {dlnode} -- [description]
        """
        node.next = self.nil.next
        self.nil.next.prev = node
        self.nil.next = node
        node.prev = self.nil

    def append(self, node):
        """append

        Arguments:
            node {dlnode} -- [description]
        """
        node.prev = self.nil.prev
        self.nil.prev.next = node
        self.nil.prev = node
        node.next = self.nil

    def popleft(self):
        """pop left

        Returns:
            dlnode -- [description]
        """
        res = self.nil.next
        self.nil.next = res.next
        self.nil.next.prev = self.nil
        return res

    def pop(self):
        """pop

        Returns:
            dlnode -- [description]
        """
        res = self.nil.prev
        self.nil.prev = res.prev
        self.nil.prev.next = self.nil
        return res

    def detach(self, node):
        """detach

        Arguments:
            node {dlnode} -- [description]
        """
        node.detach()

    def __iter__(self):
        """iterable

        Returns:
            dllist -- itself
        """
        self.cur = self.nil.next
        return self

    def __next__(self):
        """next

        Raises:
            StopIteration -- [description]

        Returns:
            dlnode -- [description]
        """
        if self.cur != self.nil:
            res = self.cur
            self.cur = self.cur.next
            return res
        else:
            raise StopIteration
