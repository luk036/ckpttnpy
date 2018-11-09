"""
bounded priority queue
"""

from collections import deque
from dllist import dllist, dlnode

class bpqueue:
    def __init__(self, a, b):
        self.offset = a - 1
        self.high = b - self.offset
        self.max = 0
        self.bucket = list(dllist() for _ in range(self.high + 1))
        self.bucket[0] = dllist() # sentinet
        self.bucket[0].append(dlnode())

    def get_key(self, it):
        pass

    def get_max(self):
        return self.max + self.offset

    def is_empty(self):
        return self.max == 0

    def clear(self):
        while self.max > 0:
            self.bucket[self.max].clear()
            self.max -= 1

    def append(self, it, k):
        key = k - self.offset
        if self.max < key:
            self.max = key
        it.key = key
        self.bucket[key].append(it)

    def popleft(self):
        res = self.bucket[self.max].popleft()
        while self.bucket[self.max].is_empty():
            self.max -= 1
        return res

    def decrease_key(self, it, m):
        self.bucket[it.key].detach(it)
        it.key -= m
        self.bucket[it.key].append(it) # FIFO
        while self.bucket[self.max].is_empty():
            self.max -= 1

    def increase_key(self, it, m):
        self.bucket[it.key].detach(it)
        it.key += m
        self.bucket[it.key].appendleft(it) # LIFO
        if self.max < it.key:
            self.max = it.key

    def modify_key(self, it, m):
        if m > 0:
            self.increase_key(it, m)
        elif m < 0:
            self.decrease_key(it, m)

    def detach(self, it):
        self.bucket[it.key].detach(it)
        while self.bucket[self.max].is_empty():
            self.max -= 1

    def __iter__(self):
        self.curkey = self.max
        self.curitem = iter(self.bucket[self.curkey])
        return self

    def __next__(self):
        while self.curkey > 0:
            try:
                res = next(self.curitem)
                return res
            except StopIteration:
                self.curkey -= 1
                self.curitem = iter(self.bucket[self.curkey])
        raise StopIteration
            
