class shift_list(list):
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
    a = shift_list([i*i for i in range(10)])
    a.set_start(4)
    print(a[4])
    for i in a:
        print(i)
