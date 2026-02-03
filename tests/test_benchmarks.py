"""
Performance benchmarks for ckpttnpy using pytest-benchmark.

These tests measure and track performance of key algorithms over time.
"""

from ckpttnpy.skeleton import fib


def test_fibonacci_performance(benchmark):
    """Benchmark Fibonacci function performance."""
    benchmark(fib, 30)


def test_fibonacci_performance_large(benchmark):
    """Benchmark Fibonacci function with larger input."""
    benchmark(fib, 40)
