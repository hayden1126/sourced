"""sourced — Claude Code framework for academic papers."""
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("sourced")
except PackageNotFoundError:  # editable / not yet installed
    try:
        from ._version import __version__
    except ImportError:
        __version__ = "0.0.0+unknown"

__all__ = ["__version__"]
