from collections.abc import MutableMapping
from typing import Iterator, TypeVar, List

T = TypeVar("T")


class Lict(MutableMapping[int, T]):
    """Lict

    The `Lict` class is a custom implementation of a mutable mapping with integer keys and generic
    values, which adapts a list to behave like a dictionary.
    """

    def __init__(self, lst: List[T]) -> None:
        """
        The function is a constructor for a dictionary-like adaptor for a list.
        
        :param lst: The `lst` parameter is a list that is being passed to the `__init__` method. It is used
        to initialize the `self.lst` attribute of the class
        :type lst: List[T]
        """
        self.rng = range(len(lst))
        self.lst = lst

    def __getitem__(self, key: int) -> T:
        """
        This function allows you to access an element in a Lict object by its index.
        
        :param key: The `key` parameter is of type `int` and it represents the index of the element that you
        want to retrieve from the list
        :type key: int
        :return: The `__getitem__` method is returning the item at the specified index in the `lst`
        attribute.

        Examples:
            >>> a = Lict([1, 4, 3, 6])
            >>> a[2]
            3
        """
        return self.lst.__getitem__(key)

    def __setitem__(self, key: int, new_value: T):
        """_summary_

        Args:
            key (_type_): _description_
            new_value (_type_): _description_

        Examples:
            >>> a = Lict([1, 4, 3, 6])
            >>> a[2] = 7
            >>> print(a[2])
            7
        """
        self.lst.__setitem__(key, new_value)

    def __delitem__(self, _):
        """(You really should not delete item from Lict)

        Args:
            key (_type_): _description_

        Returns:
            _type_: _description_
        """
        raise NotImplementedError()

    def __iter__(self) -> Iterator:
        """_summary_

        Returns:
            _type_: _description_

        Yields:
            Iterator: _description_

        Examples:
            >>> a = Lict([1, 4, 3, 6])
            >>> for i in a:
            ...     print(i)
            0
            1
            2
            3
        """
        return iter(self.rng)

    def __contains__(self, value) -> bool:
        """_summary_

        Args:
            value (_type_): _description_

        Returns:
            bool: _description_

        Examples:
            >>> a = Lict([1, 4, 3, 6])
            >>> 2 in a
            True
        """
        return value in self.rng

    def __len__(self) -> int:
        """_summary_

        Returns:
            _type_: _description_

        Examples:
            >>> a = Lict([1, 4, 3, 6])
            >>> len(a)
            4
        """
        return len(self.rng)

    def values(self):
        """_summary_

        Returns:
            _type_: _description_

        Yields:
            Iterator: _description_

        Examples:
            >>> a = Lict([1, 4, 3, 6])
            >>> for i in a.values():
            ...     print(i)
            1
            4
            3
            6
        """
        return iter(self.lst)

    def items(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return enumerate(self.lst)


if __name__ == "__main__":
    a = Lict([0] * 8)
    for i in a:
        a[i] = i * i
    for i, v in a.items():
        print(f'{i}: {v}')
    print(3 in a)
