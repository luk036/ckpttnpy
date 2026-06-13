import pytest

from ckpttnpy.skeleton import fib, main

__author__ = "Wai-Shing Luk"
__copyright__ = "Wai-Shing Luk"
__license__ = "MIT"


def test_fib() -> None:
    """API Tests"""
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(7) == 13
    with pytest.raises(AssertionError):
        fib(-10)


def test_main(capsys) -> None:
    """CLI Tests"""
    # capsys is a pytest fixture that allows asserts agains stdout/stderr
    # https://docs.pytest.org/en/stable/capture.html
    main(["7"])
    captured = capsys.readouterr()
    assert "The 7-th Fibonacci number is 13" in captured.out


def test_run(capsys) -> None:
    """Test run() entry point which calls main(sys.argv[1:])."""
    import sys

    from ckpttnpy.skeleton import run

    # Monkey-patch sys.argv
    original_argv = sys.argv
    try:
        sys.argv = ["skeleton.py", "7"]
        run()
        captured = capsys.readouterr()
        assert "The 7-th Fibonacci number is 13" in captured.out
    finally:
        sys.argv = original_argv
