from dllist import dllist, dlnode
from bpqueue import bpqueue

def test_bpqueue():
    bpq1 = bpqueue(-10, 10)
    bpq2 = bpqueue(-10, 10)

    assert bpq1.is_empty()

    d = dlnode()
    e = dlnode()
    f = dlnode()

    assert  d.key == None

    bpq1.append(e, 3)
    bpq1.append(f, -10)
    bpq1.append(d, 5)

    bpq2.append(bpq1.popleft(), -6) # d
    bpq2.append(bpq1.popleft(), 3)
    bpq2.append(bpq1.popleft(), 0)

    bpq2.increase_key(d, 15)
    bpq2.decrease_key(d, 3)
    assert bpq1.is_empty()
    assert bpq2.get_max() == 6

    nodelist = list(dlnode() for _ in range(10))
    gainlist = list(2*i - 10 for i in range(10))
    bpq1.appendfrom(zip(nodelist, gainlist))
    
    count = 0
    for _ in bpq1:
        count += 1
    assert count == 10