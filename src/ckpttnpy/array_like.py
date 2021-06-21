from itertools import repeat


class repeat_array:
    """list with arbitrary range"""
    def __init__(self, value, size):
        self.value = value
        self.size = size

    def __getitem__(self, key):
        return self.value

    def __len__(self):
        return self.size

    def __iter__(self):
        return repeat(self.value, self.size)


class shift_array(list):
    """list with arbitrary range"""
    def __new__(cls, *args, **kwargs):
        return list.__new__(cls, *args, **kwargs)

    def __init__(self, *args, **kwargs):
        self.start = 0
        list.__init__(self, *args, **kwargs)

    def set_start(self, start):
        self.start = start

    def __getitem__(self, key):
        return list.__getitem__(self, key - self.start)

    def __setitem__(self, key, newValue):
        list.__setitem__(self, key - self.start, newValue)


if __name__ == '__main__':
    a = repeat_array(1, 10)
    print(a[4])
    for i in a:
        print(i)
