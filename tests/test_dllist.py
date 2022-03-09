from ckpttnpy.dllist import Dllist, dllink


def test_dllink():
    L1 = Dllist()
    L2 = Dllist()
    d = dllink()
    e = dllink()
    f = dllink()
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
