from itertools import repeat


class RepeatArray:
    """list with arbitrary range"""

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
    """list with arbitrary range"""

    def __new__(cls, *args, **kwargs):
        """[summary]

        Returns:
            [type]: [description]
        """
        return list.__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        self.start = 0
        list.__init__(self, *args, **kwargs)

    def set_start(self, start):
        """[summary]

        Args:
            start ([type]): [description]
        """
        self.start = start

    def __getitem__(self, key):
        """[summary]

        Args:
            key ([type]): [description]

        Returns:
            [type]: [description]
        """
        return list.__getitem__(self, key - self.start)

    def __setitem__(self, key, newValue):
        """[summary]

        Args:
            key ([type]): [description]
            newValue ([type]): [description]
        """
        list.__setitem__(self, key - self.start, newValue)

    def items(self):
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
