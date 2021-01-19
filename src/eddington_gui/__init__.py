"""A gui library wrapping Eddington."""

has_matplotlib = False  # pylint: disable=invalid-name
try:
    import matplotlib

    matplotlib.use("agg")
    has_matplotlib = True  # pylint: disable=invalid-name
except ImportError:
    pass

__version__ = "0.0.8.dev0"
__author__ = "Sagi Shadur"
__year__ = "2020-2021"
