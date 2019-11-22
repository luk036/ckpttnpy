# -*- coding: utf-8 -*-


class dllink:
    """doubly linked node (that may also be a "head" a list)

    A Doubly-linked List class. This class simply contains a link of
    node's. By adding a "head" node (sentinel), deleting a node is
    extremely fast (see "Introduction to Algorithm"). This class does
    not keep the length information as it is not necessary for the FM
    algorithm. This saves memory and run-time to update the length
    information. Note that this class does not own the list node. They
    are supplied by the caller in order to better reuse the nodes.
    """
    __slots__ = ('key', 'next', 'prev', 'index')

    def __init__(self, index=None):
        """initialization

        Keyword Arguments:
            index (type):  description (default: {None})
        """
        self.key = 0
        self.next = self.prev = self
        self.index = index

    def detach(self):
        """detach from a list """
        assert self.next
        n = self.next
        p = self.prev
        p.next = n
        n.prev = p

    def lock(self):
        """lock the node (and don't append it to any list) """
        self.next = None

    def is_locked(self):
        """whether the node is locked

        Returns:
            bool:  description
        """
        return self.next is None

    def is_empty(self):
        """whether the list is empty

        Returns:
            bool:  description
        """
        return self.next == self

    def clear(self):
        """clear"""
        self.next = self.prev = self

    def appendleft(self, node):
        """append the node to the front

        Arguments:
            node (dllink):  description
        """
        node.next = self.next
        self.next.prev = node
        self.next = node
        node.prev = self

    def append(self, node):
        """append the node to the back

        Arguments:
            node (dllink):  description
        """
        node.prev = self.prev
        self.prev.next = node
        self.prev = node
        node.next = self

    def popleft(self):
        """pop a node from the front

        Returns:
            dllink:  description
        """
        res = self.next
        self.next = res.next
        self.next.prev = self
        return res

    def pop(self):
        """pop a node from the back

        Returns:
            dllink:  description
        """
        res = self.prev
        self.prev = res.prev
        self.prev.next = self
        return res

    def __iter__(self):
        """iterable

        Returns:
            dllink:  itself
        """
        cur = self.next
        while cur != self:
            yield cur
            cur = cur.next


# class dll_iterator:
#     """List iterator

#     Traverse the list from the first item. Usually it is safe
#     to attach/detach list items during the iterator is active.
#     """

#     def __init__(self, link):
#         """Initialization

#         Arguments:
#             link (dllink):  description
#         """
#         self.link = link
#         self.cur = link.next

#     def next(self):
#         """Get the next item

#         Raises:
#             StopIteration:  description

#         Returns:
#             dllink:  the next item
#         """
#         if self.cur != self.link:
#             res = self.cur
#             self.cur = self.cur.next
#             return res
#         else:
#             raise StopIteration

#     def __next__(self):
#         """[summary]

#         Returns:
#             dtype:  description
#         """
#         return self.next()
