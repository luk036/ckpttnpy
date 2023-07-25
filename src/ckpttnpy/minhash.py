import numpy as np


class MinHash(object):
    """The MinHash class is a Python implementation of the MinHash algorithm, which is used to estimate the
    similarity between sets by hashing their elements.

    Examples:
        >>> m1 = MinHash(k=10)
    """

    def __init__(self, k, seed=10):
        """
        The function initializes an object with a given value for k and a seed, and generates random masks
        and hashes.

        :param k: The parameter `k` represents the number of hash functions to be used
        :param seed: The `seed` parameter is used to initialize the random number generator. By setting a
        specific seed value, you can ensure that the random numbers generated are reproducible. If you use
        the same seed value, you will get the same sequence of random numbers every time you run the code,
        defaults to 10 (optional)

        Examples:
            >>> m1 = MinHash(k=10)
            >>> m2 = MinHash(k=10, seed=10)
            >>> m3 = MinHash(k=10, seed=10)
            >>> m1.jaccard(m2)
            1.0
            >>> m1.jaccard(m3)
            1.0
            >>> m2.jaccard(m3)
            1.0
            >>> m1.add(1)
            >>> m2.add(1)
            >>> m1.jaccard(m2)
            1.0
            >>> m1.jaccard(m3)
            0.0
            >>> m2.jaccard(m3)
            0.0
            >>> m1.add(2)
            >>> m2.add(2)
            >>> m1.jaccard(m2)
            1.0
            >>> m1.jaccard(m3)
            0.0
            >>> m2.jaccard(m3)
            0.0

        """
        self._k = k
        self._seed = seed

        minint = np.iinfo(np.int64).min
        maxint = np.iinfo(np.int64).max

        self._masks = np.random.RandomState(seed=self._seed).randint(
            minint, maxint, self._k
        )

        self._hashes = np.empty(self._k, dtype=np.int64)
        self._hashes.fill(maxint)

    def add(self, v):
        """
        The function calculates the minimum hash value between the current hash values and the bitwise XOR
        of the input value and the masks.

        :param v: The parameter `v` represents the value that you want to add to the data structure
        """
        hashes = np.bitwise_xor(self._masks, hash(v))
        self._hashes = np.minimum(self._hashes, hashes)

    def jaccard(self, other):
        """
        The function calculates the Jaccard similarity between two MinHash objects.

        :param other: The `other` parameter is another MinHash object that we want to compare similarity
        with
        :return: the Jaccard similarity between two MinHashes.
        """
        if np.any(self._masks != other._masks):
            raise Exception(
                "Can only calculate similarity "
                "between MinHashes with the same hash "
                "functions."
            )
        return (self._hashes == other._hashes).sum() / float(self._k)
