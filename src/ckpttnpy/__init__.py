from importlib.metadata import PackageNotFoundError, version

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

# Import MultiFPGAPartMgr to make it available at package level
from .MultiFPGAPartMgr import MultiFPGAGainCalc, MultiFPGAPartMgr

__all__ = ["MultiFPGAGainCalc", "MultiFPGAPartMgr"]
