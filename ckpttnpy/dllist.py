class dlnode:
    def __init__(self, next=None, prev=None, key=None):
        self.next = next
        self.prev = prev
        self.key = key

    def detach(self):
        n = self.next
        p = self.prev
        p.next = n
        p.prev = p


class dllist:
    def __init__(self):
        self.nil = dlnode()
        self.head = self.tail = self.nil
        self.cur = None

    def is_empty(self):
        return self.head == self.nil

    def clear(self):
        self.head = self.tail = self.nil

    def appendleft(self, node):
        if self.head == self.nil: # empty
            self.head = self.tail = node
            node.next = node.prev = self.nil
        else:
            node.next = self.head
            self.head.prev = node
            self.head = node
            node.prev = self.nil

    def append(self, node):
        if self.head == self.nil: # empty
            self.head = self.tail = node
            node.next = node.prev = self.nil
        else:
            node.prev = self.tail
            self.tail.next = node
            self.tail = node
            node.next = self.nil

    def popleft(self):
        res = self.head
        self.head = res.next
        self.head.prev = self.nil
        if self.head == self.nil: # empty
            self.tail = self.nil
        return res

    def pop(self):
        res = self.tail
        self.tail = res.prev
        self.tail.next = self.nil
        if self.tail == self.nil: # empty
            self.head = self.nil
        return res

    def detach(self, node):
        if node.next == self.nil and node.prev == self.nil:
            self.head = self.tail = self.nil
        node.detach()

    def __iter__(self):
        self.cur = self.head
        return self

    def __next__(self):
        if self.cur != self.nil:
            res = self.cur
            self.cur = self.cur.next
            return res
        else:
            raise StopIteration
            
