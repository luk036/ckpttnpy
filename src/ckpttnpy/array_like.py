from itertools import repeat


class RepeatArray:
    """list with arbitrary range

    The RepeatArray class allows for the repetition of elements in an array.
    """

    def __init__(self, value, size):
        """[summary]

        Args:
            value ([type]): [description]
            size ([type]): [description]
        """
        self.value = value
        self.size = size

    def __getitem__(self, _):  # key is ignored
        """[summary]

        Args:
            key ([type]): [description]

        Returns:
            [type]: [description]
        """
        return self.value

    def __len__(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        return self.size

    def __iter__(self):
        """[summary]

        Returns:
            [type]: [description]
        """
        return repeat(self.value, self.size)

    def get(self, _):  # defaultvalue is ignored
        return self.value


class ShiftArray(list):
    """ShiftArray
    The `ShiftArray` class is a subclass of the built-in `list` class in Python. It extends the
    functionality of a list by allowing the user to set a starting index for the list.
    list with arbitrary range
    """

    def __new__(cls, *args, **kwargs):
        """
        The function overrides the `__new__` method of the `list` class in Python.
        
        :param cls: The `cls` parameter in the `__new__` method refers to the class itself. It is
        automatically passed as the first argument when the method is called
        :return: The `__new__` method is returning a new instance of the class `cls` as a list.
        """
        return list.__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        """
        The function is a constructor that initializes an object with a start value of 0 and calls the
        constructor of the parent class "list".
        """
        self.start = 0
        list.__init__(self, *args, **kwargs)

    def set_start(self, start):
        """
        The function sets the value of the "start" attribute.
        
        :param start: The `start` parameter is a value that will be assigned to the `start` attribute of the
        object
        """
        self.start = start

    def __getitem__(self, key):
        """
        The `__getitem__` function returns the item at the specified index, adjusted by the `start`
        attribute.
        
        :param key: The `key` parameter is the index or slice object used to access the elements of the
        list. It can be an integer index or a slice object that specifies a range of indices
        :return: The method is returning the item at the specified index in the list.
        """
        return list.__getitem__(self, key - self.start)

    def __setitem__(self, key, newValue):
        """
        The `__setitem__` function is used to set the value of an item in a list-like object, adjusting the
        index based on the start value.
        
        :param key: The key parameter represents the index of the element in the list that you want to set a
        new value for
        :param newValue: The `newValue` parameter is the value that you want to set for the given key in the
        list
        """
        list.__setitem__(self, key - self.start, newValue)

    def items(self):
        """
        The `items` function returns an iterator that yields tuples containing the index and value of each
        element in the object.
        :return: The `items` method is returning an iterator that yields tuples containing the index
        (starting from `self.start`) and the corresponding value for each element in the object.
        """
        return iter((i + self.start, v) for i, v in enumerate(self))


if __name__ == "__main__":
    arr = RepeatArray(1, 10)
    print(arr[4])
    for i in arr:
        print(i)

    b = ShiftArray([9, 4, 1, 3, 8, 7, 6, 5])
    b.set_start(10)
    print(b[14])
    for i in b:
        print(i)
