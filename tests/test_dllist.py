from ckpttnpy.dllist import Dllink, Dllist


def test_dllink():
    L1 = Dllist(99)
    L2 = Dllist(99)
    d = Dllink(1)
    e = Dllink(2)
    f = Dllink(3)
    # assert L1.next == L1  # is_empty()

    L1.appendleft(e)
    assert not L1.is_empty()

    L1.appendleft(f)
    L1.append(d)
    L2.append(L1.pop())
    L2.append(L1.popleft())
    assert not L1.is_empty()
    assert not L2.is_empty()
    e.detach()
    assert L1.is_empty()

    count = 0
    for _ in L2:
        count += 1
    assert count == 2
