"""Shared helpers for driving the partitioners.

Small utilities that used to be copy-pasted across ``cli.py``, the experiment
scripts, the benchmarks and the tests:

* :func:`make_init_part` — build a random initial partition in whatever
  representation the netlist expects (``list`` for ``range`` modules, ``dict``
  for ``list`` modules).
* :func:`random_init_part` — in-place randomization that honours fixed modules.
* :func:`multi_start` — best-of-N driver.

Nothing here imports the rest of ``ckpttnpy``, so it stays dependency-free.
"""

from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

Part = Union[Dict[Any, int], List[int]]


def make_init_part(hyprgraph: Any, k: int, rng: Any) -> Part:
    """Return a random initial partition for *hyprgraph*.

    The representation matches what the partition managers expect: a ``list``
    when the netlist enumerates modules with a ``range``, otherwise a
    ``{module: part}`` dict.

    :param hyprgraph: netlist to partition
    :param k: number of partitions (assignments are drawn from ``0..k-1``)
    :param rng: any object exposing ``randrange`` (a ``random.Random`` instance
        or the ``random`` module itself)
    :returns: a fresh ``Part``
    """
    if isinstance(hyprgraph.modules, range):
        return [rng.randrange(k) for _ in hyprgraph]
    if isinstance(hyprgraph.modules, list):
        return {v: rng.randrange(k) for v in hyprgraph}
    raise NotImplementedError


def random_init_part(
    part: List[int],
    num_modules: int,
    num_parts: int,
    module_fixed: Set[int],
    rng: Any,
) -> None:
    """Randomize *part* in place for every module not in *module_fixed*."""
    for i in range(num_modules):
        if i not in module_fixed:
            part[i] = rng.randint(0, num_parts - 1)


def multi_start(
    n_starts: int, run_fn: Callable[[], Tuple[int, Part]]
) -> Tuple[int, Part]:
    """Call *run_fn* ``n_starts`` times and keep the lowest-cost result.

    :param n_starts: number of independent starts (``>= 1``)
    :param run_fn: a zero-argument callable returning ``(cost, part)``; it must
        build a *fresh* part on every call
    :returns: ``(best_cost, best_part)``
    """
    best_cost: Optional[int] = None
    best_part: Part = []
    for _ in range(n_starts):
        cost, part = run_fn()
        if best_cost is None or cost < best_cost:
            best_cost, best_part = cost, part.copy()
    assert best_cost is not None
    return best_cost, best_part
