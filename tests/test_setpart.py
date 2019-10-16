from ckpttnpy.set_partition import set_partition, stirling2nd


def test_setpart_odd():
    n, k = 10, 5
    b = [0 for i in range(n-k+1)] + list(range(k))
    cnt = 1
    for x, y in set_partition(n, k):
        # old = b[x]
        b[x] = y
        cnt += 1
        # print(b[1:], ": Move {} from block {} to {}".format(x, old, y))
    assert stirling2nd(n, k) == cnt
    # print("Done.")


def test_setpart_even():
    n, k = 9, 4
    b = [0 for i in range(n-k+1)] + list(range(k))
    cnt = 1
    for x, y in set_partition(n, k):
        # old = b[x]
        b[x] = y
        cnt += 1
        # print(b[1:], ": Move {} from block {} to {}".format(x, old, y))
    assert stirling2nd(n, k) == cnt
    # print("Done.")
