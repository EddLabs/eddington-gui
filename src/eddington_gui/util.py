"""Utility methods."""


def value_or_none(value: str):
    """
    Return string value if not empty. Otherwise, returns None.

    :param value: a string value to convert into a None if its empty
    :type value: str
    :return: None or the value itself
    :rtype: None or str
    """
    if value.strip() == "":
        return None
    return value
