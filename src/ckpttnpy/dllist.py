class Dllink:
    """doubly linked node (that may also be a "head" a list)

    A Doubly-linked List class. This class simply contains a link of
    node's. By adding a "head" node (sentinel), deleting a node is
    extremely fast (see "Introduction to Algorithm"). This class does
    not keep the length information as it is not necessary for the FM
    algorithm. This saves memory and run-time to update the length
    information. Note that this class does not own the list node. They
    are supplied by the caller in order to better reuse the nodes.
    """

    __slots__ = ("next", "prev", "data")

    def __init__(self, data=None):
        """initialization

        Keyword Arguments:
            index (type):  description (default: {None})

        Examples:
            >>> a = Dllink(3)
            >>> a.data
            3
        """
        self.next = self.prev = self
        # self.key = 0
        self.data = data

    def is_locked(self):
        """whether the node is locked

        Returns:
            bool:  description

        Examples:
            >>> a = Dllink(3)
            >>> a.is_locked()
            False
        """
        return self.next is None

    def lock(self):
        """lock the node (and don't append it to any list)

        Examples:
            >>> a = Dllink(3)
            >>> a.lock()
            >>> a.is_locked()
            True
        """
        self.next = None

    def appendleft(self, node):
        """append the node to the front

        Arguments:
            node (Dllink):  description

        Examples:
            >>> a = Dllink(3)
            >>> b = Dllink(4)
            >>> a.appendleft(b)
        """
        node.next = self.next
        self.next.prev = node
        self.next = node
        node.prev = self

    def append(self, node):
        """append the node to the back

        Arguments:
            node (Dllink):  description

        Examples:
            >>> a = Dllink(3)
            >>> b = Dllink(4)
            >>> a.append(b)
        """
        node.prev = self.prev
        self.prev.next = node
        self.prev = node
        node.next = self

    def popleft(self):
        """pop a node from the front

        Returns:
            Dllink:  description

        Examples:
            >>> a = Dllink(3)
            >>> b = Dllink(4)
            >>> a.appendleft(b)
            >>> c = a.popleft()
            >>> b == c
            True
        """
        res = self.next
        self.next = res.next
        self.next.prev = self
        return res

    def pop(self):
        """pop a node from the back

        Returns:
            Dllink:  description

        Examples:
            >>> a = Dllink(3)
            >>> b = Dllink(4)
            >>> a.append(b)
            >>> c = a.pop()
            >>> b == c
            True
        """
        res = self.prev
        self.prev = res.prev
        self.prev.next = self
        return res

    def detach(self):
        """detach from a list

        Examples:
            >>> a = Dllink(3)
            >>> b = Dllink(4)
            >>> a.append(b)
            >>> b.detach()
        """
        assert self.next
        n = self.next
        p = self.prev
        p.next = n
        n.prev = p

    # def __iter__(self):
    #     """iterable

    #     Returns:
    #         Dllink:  itself
    #     """
    #     cur = self.next
    #     while cur != self:
    #         yield cur
    #         cur = cur.next


# -*- coding: utf-8 -*-


class Dllist:
    """doubly linked node (that may also be a "head" a list)

    A Doubly-linked List class. This class simply contains a link of
    node's. By adding a "head" node (sentinel), deleting a node is
    extremely fast (see "Introduction to Algorithm"). This class does
    not keep the length information as it is not necessary for the FM
    algorithm. This saves memory and run-time to update the length
    information. Note that this class does not own the list node. They
    are supplied by the caller in order to better reuse the nodes.
    """

    __slots__ = "head"

    def __init__(self, data=None):
        """initialization

        Keyword Arguments:
            index (type):  description (default: {None})

        Examples:
            >>> a = Dllist(3)
            >>> a.head.data
            3
        """
        self.head = Dllink(data)

    def is_empty(self):
        """whether the list is empty

        Returns:
            bool:  description

        Examples:
            >>> a = Dllist(3)
            >>> a.is_empty()
            True
        """
        return self.head.next == self.head

    def clear(self):
        """clear

        Examples:
            >>> a = Dllist(3)
            >>> a.clear()
            >>> a.is_empty()
            True
        """
        self.head.next = self.head.prev = self.head

    def appendleft(self, node):
        """append the node to the front

        Arguments:
            node (Dllink):  description

        Examples:
            >>> a = Dllist(3)
            >>> b = Dllink(4)
            >>> a.appendleft(b)
            >>> a.is_empty()
            False
        """
        self.head.appendleft(node)

    def append(self, node):
        """append the node to the back

        Arguments:
            node (Dllink):  description

        Examples:
            >>> a = Dllist(3)
            >>> b = Dllink(4)
            >>> a.append(b)
            >>> a.is_empty()
            False
        """
        self.head.append(node)

    def popleft(self):
        """pop a node from the front

        Returns:
            Dllink:  description

        Examples:
            >>> a = Dllist(3)
            >>> b = Dllink(4)
            >>> a.appendleft(b)
            >>> c = a.popleft()
            >>> b == c
            True
        """
        return self.head.popleft()

    def pop(self):
        """pop a node from the back

        Returns:
            Dllink:  description

        Examples:
            >>> a = Dllist(3)
            >>> b = Dllink(4)
            >>> a.append(b)
            >>> c = a.pop()
            >>> b == c
            True
        """
        return self.head.pop()

    # def __iter__(self):
    #     """iterable

    #     Returns:
    #         Dllink:  itself
    #     """
    #     cur = self.next
    #     while cur != self:
    #         yield cur
    #         cur = cur.next

    def __iter__(self):
        """iterable

        Returns:
            Dllink:  itself
        """
        return DllIterator(self.head)


class DllIterator:
    """List iterator

    Traverse the list from the first item. Usually it is safe
    to attach/detach list items during the iterator is active.
    """

    def __init__(self, link):
        """Initialization

        Arguments:
            link (Dllink):  description

        Examples:
            >>> a = Dllist(3)
            >>> it = iter(a)
        """
        self.link = link
        self.cur = link.next

    def __next__(self):
        """Get the next item

        Raises:
            StopIteration:  description

        Returns:
            Dllink:  the next item

        Examples:
            >>> a = Dllist(3)
            >>> b = Dllink(4)
            >>> a.append(b)
            >>> cursor = iter(a)
            >>> c = next(cursor)
            >>> b == c
            True
        """
        if self.cur != self.link:
            res = self.cur
            self.cur = self.cur.next
            return res
        else:
            raise StopIteration

    # def __next__(self):
    #     """[summary]

    #     Returns:
    #         dtype:  description
    #     """
    #     return self.next()


if __name__ == "__main__":
    import doctest

    doctest.testmod()
