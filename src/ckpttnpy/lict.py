from typing import Iterator, List, MutableMapping, TypeVar

T = TypeVar("T")


class Lict(MutableMapping[int, T]):
    """Lict

    The `Lict` class is a custom implementation of a mutable mapping with integer keys and generic
    values, which adapts a list to behave like a dictionary.
    """

    def __init__(self, lst: List[T]) -> None:
        """
        The function is a constructor for a dictionary-like adaptor for a list.

        :param lst: The `lst` parameter is a list that is being passed to the `__init__` method. It is used to initialize the `self.lst` attribute of the class
        :type lst: List[T]
        """
        self.rng = range(len(lst))
        self.lst = lst

    def __getitem__(self, key: int) -> T:
        """
        This function allows you to access an element in a Lict object by its index.

        :param key: The `key` parameter is of type `int` and it represents the index of the element that you want to retrieve from the list
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
        """
        This function sets the value at a given index in a list-like object.

        :param key: The key parameter represents the index at which the new value should be set in the list
        :type key: int
        :param new_value: The `new_value` parameter is the value that you want to assign to the element at the specified key in the list
        :type new_value: T

        Examples:
            >>> a = Lict([1, 4, 3, 6])
            >>> a[2] = 7
            >>> print(a[2])
            7
        """
        self.lst.__setitem__(key, new_value)

    def __delitem__(self, _):
        """
        The __delitem__ function raises a NotImplementedError and provides a docstring explaining that
        deleting items from Lict is not recommended.

        :param _: The underscore (_) is typically used as a placeholder for a variable or value that is not going to be used or referenced in the code. In this case, it is used as a placeholder for the key parameter in the __delitem__ method
        """
        raise NotImplementedError()

    def __iter__(self) -> Iterator:
        """
        The function returns an iterator that yields elements from the `rng` attribute of the object.
        :return: The `iter(self.rng)` is being returned.

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
        """
        The `__contains__` function checks if a given value is present in the `rng` attribute of the object.

        :param value: The `value` parameter represents the value that we want to check if it is present in the `self.rng` attribute
        :return: The method is returning a boolean value, indicating whether the given value is present in the `self.rng` attribute.

        Examples:
            >>> a = Lict([1, 4, 3, 6])
            >>> 2 in a
            True
        """
        return value in self.rng

    def __len__(self) -> int:
        """
        This function returns the length of the `rng` attribute of the object.
        :return: The `len` function is returning the length of the `self.rng` attribute.

        Examples:
            >>> a = Lict([1, 4, 3, 6])
            >>> len(a)
            4
        """
        return len(self.rng)

    def values(self):
        """
        The `values` function returns an iterator that yields the elements of the `lst` attribute of the
        `Lict` object.
        :return: The `values` method returns an iterator object.

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
        """
        The function returns an enumeration of the items in the list.
        :return: The `items` method is returning an enumeration of the `lst` attribute.
        """
        return enumerate(self.lst)


if __name__ == "__main__":
    a = Lict([0] * 8)
    for i in a:
        a[i] = i * i
    for i, v in a.items():
        print(f"{i}: {v}")
    print(3 in a)
