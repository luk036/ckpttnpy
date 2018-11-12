from dllist import dllist, dlnode


def test_dllist():
    L1 = dllist()
    L2 = dllist()
    d = dlnode()
    e = dlnode()
    f = dlnode()
    assert L1.is_empty()

    L1.appendleft(e)
    assert not L1.is_empty()

    L1.appendleft(f)
    L1.append(d)
    L2.append(L1.pop())
    L2.append(L1.popleft())
    assert not L1.is_empty()
    assert not L2.is_empty()

    count = 0
    for _ in L2:
        count += 1
    assert count == 2
