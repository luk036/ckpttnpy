import numpy as np


class MinHash(object):

    def __init__(self, k, seed=10):

        self._k = k
        self._seed = seed

        minint = np.iinfo(np.int64).min
        maxint = np.iinfo(np.int64).max

        self._masks = (np.random.RandomState(seed=self._seed)
                       .randint(minint, maxint, self._k))

        self._hashes = np.empty(self._k, dtype=np.int64)
        self._hashes.fill(maxint)

    def add(self, v):

        hashes = np.bitwise_xor(self._masks, hash(v))

        self._hashes = np.minimum(self._hashes, hashes)

    def jaccard(self, other):

        if np.any(self.masks != other._masks):
            raise Exception('Can only calculate similarity '
                            'between MinHashes with the same hash '
                            'functions.')

        return (self._hashes == other._hashes).sum() / float(self._k)
