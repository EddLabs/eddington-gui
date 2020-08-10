"""Utility methods."""


def value_or_none(value):
    """Return string value if not empty. Otherwise, returns None."""
    if value == "":
        return None
    return value
