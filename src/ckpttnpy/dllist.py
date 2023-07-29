from typing import Generic, TypeVar

T = TypeVar("T")


class Dllink(Generic[T]):
    """The `Dllink` class is a doubly linked list implementation that
    does not keep track of the length of the list.

    A Doubly-linked List class. This class simply contains a link of
    node's. By adding a "head" node (sentinel), deleting a node is
    extremely fast (see "Introduction to Algorithm"). This class does
    not keep the length information as it is not necessary for the FM
    algorithm. This saves memory and run-time to update the length
    information. Note that this class does not own the list node. They
    are supplied by the caller in order to better reuse the nodes.

    Examples:
        >>> a = Dllink(3)
    """

    __slots__ = ("next", "prev", "data")

    next: "Dllink[T]"
    prev: "Dllink[T]"
    data: T

    def __init__(self, data: T) -> None:
        """
        The `__init__` function initializes a `Dllink` object with a given data value and sets the `next`
        and `prev` attributes to point to itself.

        :param data: The `data` parameter is of type `T` and represents the data that will be stored in the `Dllink` object. The `T` type is a generic type, meaning it can be replaced with any specific type when creating an instance of the `Dllink` class
        :type data: T

        Examples:
            >>> a = Dllink(3)
            >>> a.data
            3
        """
        self.next = self.prev = self
        self.data = data

    def is_locked(self) -> bool:
        """
        The `is_locked` function returns `True` if the node is locked, and `False` otherwise.
        :return: The method is returning a boolean value indicating whether the node is locked or not.

        Examples:
            >>> a = Dllink(3)
            >>> a.is_locked()
            True
        """
        return self.next == self

    def lock(self) -> None:
        """
        The `lock` function locks a node by setting its `next` attribute to itself.
        (and don't append it to any list)

        Examples:
            >>> a = Dllink(3)
            >>> a.lock()
            >>> a.is_locked()
            True
        """
        self.next = self

    def appendleft(self, node: "Dllink[T]") -> None:
        """
        The `appendleft` function appends a node to the front of a doubly linked list.

        :param node: The `node` parameter is an instance of the `Dllink` class
        :type node: "Dllink[T]"

        Examples:
            >>> a = Dllink(3)
            >>> b = Dllink(4)
            >>> a.appendleft(b)
        """
        node.next = self.next
        self.next.prev = node
        self.next = node
        node.prev = self

    def append(self, node: "Dllink[T]") -> None:
        """
        The `append` function appends a node to the back of a doubly linked list.

        :param node: The `node` parameter is an instance of the `Dllink` class
        :type node: "Dllink[T]"

        Examples:
            >>> a = Dllink(3)
            >>> b = Dllink(4)
            >>> a.append(b)
        """
        node.prev = self.prev
        self.prev.next = node
        self.prev = node
        node.next = self

    def popleft(self) -> "Dllink[T]":
        """
        The `popleft` function removes and returns the node at the front of a doubly linked list.
        :return: The method `popleft` returns a `Dllink` object.

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

    def pop(self) -> "Dllink[T]":
        """
        The `pop` function removes and returns the previous node in a doubly linked list.
        :return: The `pop` method is returning a `Dllink` object.

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

    def detach(self) -> None:
        """
        The `detach` function removes a node from a doubly linked list by updating the previous and next
        pointers of the surrounding nodes.

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


class DllIterator(Generic[T]):
    """The `DllIterator` class is a list iterator that allows traversal of a doubly
    linked list from the first item.
    """

    def __init__(self, link: Dllink[T]) -> None:
        """
        The `__init__` function initializes a Dllist object with a given link.

        :param link: The `link` parameter is of type `Dllink[T]`, which means it is a reference to a `Dllink` object. The `Dllink` class is likely a custom class that represents a node in a doubly linked list. The `T` in `Dllink[T]`
        :type link: Dllink[T]

        Examples:
            >>> a = Dllist(3)
            >>> it = iter(a)
        """
        self.link = link
        self.cur = link.next

    def __next__(self):
        """
        The `__next__` function returns the next item in a doubly linked list and raises a `StopIteration`
        exception if there are no more items.
        :return: The next item in the Dllist.

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
            raise StopIteration()


class Dllist(Generic[T]):
    """The `Dllist` class is a doubly linked list implementation that uses a "head" node for efficient
    deletion operations.

    By adding a "head" node (sentinel), deleting a node is
    extremely fast (see "Introduction to Algorithm"). This class does
    not keep the length information as it is not necessary for the FM
    algorithm. This saves memory and run-time to update the length
    information. Note that this class does not own the list node. They
    are supplied by the caller in order to better reuse the nodes.
    """

    __slots__ = "head"

    head: Dllink[T]

    def __init__(self, data: T) -> None:
        """
        The function initializes a doubly linked list with a given data value.

        :param data: The "data" parameter is the value that will be stored in the Dllink object. It can be of any type
        :type data: T

        Examples:
            >>> a = Dllist(3)
            >>> a.head.data
            3
        """
        self.head = Dllink(data)

    def is_empty(self) -> bool:
        """
        The `is_empty` function checks if a doubly linked list is empty.
        :return: a boolean value indicating whether the list is empty or not.

        Examples:
            >>> a = Dllist(3)
            >>> a.is_empty()
            True
        """
        return self.head.next == self.head

    def clear(self) -> None:
        """
        The `clear` function clears all elements from a doubly linked list.

        Examples:
            >>> a = Dllist(3)
            >>> a.clear()
            >>> a.is_empty()
            True
        """
        self.head.next = self.head.prev = self.head

    def appendleft(self, node: Dllink[T]) -> None:
        """
        The `appendleft` function appends a node to the front of a doubly linked list.

        :param node: The `node` parameter is an instance of the `Dllink` class. It represents a node that you want to append to the front of the doubly linked list
        :type node: Dllink[T]

        Examples:
            >>> a = Dllist(3)
            >>> b = Dllink(4)
            >>> a.appendleft(b)
            >>> a.is_empty()
            False
        """
        self.head.appendleft(node)

    def append(self, node: Dllink[T]) -> None:
        """
        The `append` function adds a node to the end of a doubly linked list.

        :param node: The `node` parameter is of type `Dllink[T]`, which represents a node in a doubly linked list
        :type node: Dllink[T]

        Examples:
            >>> a = Dllist(3)
            >>> b = Dllink(4)
            >>> a.append(b)
            >>> a.is_empty()
            False
        """
        self.head.append(node)

    def popleft(self):
        """
        The `popleft` function removes and returns the first node in a doubly linked list.
        :return: The `popleft` method is returning a `Dllink` object.

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
        """
        The `pop` function removes and returns the last node in a doubly linked list.
        :return: The `pop` method is returning a `Dllink` object.

        Examples:
            >>> a = Dllist(3)
            >>> b = Dllink(4)
            >>> a.append(b)
            >>> c = a.pop()
            >>> b == c
            True
        """
        return self.head.pop()

    def __iter__(self) -> DllIterator[T]:
        """
        The `__iter__` function returns an iterator object for a doubly linked list.
        :return: The `__iter__` method is returning an instance of the `DllIterator` class, passing
        `self.head` as an argument.

        Examples:
            >>> a = Dllist(3)
            >>> b = Dllink(4)
            >>> a.append(b)
            >>> it = iter(a)
            >>> c = next(it)
            >>> b == c
            True

        """
        return DllIterator(self.head)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
