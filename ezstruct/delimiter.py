"""Delimiters for fields what has 'em."""

class Delimiter(object):
    """A fixed-value boundary marker denoting the end of a string.

    Common delimiters include ``b"\x00"``, ``b","``, and ``b"\\n"`` .

    Args:
      ``delimiter``: The delimiter.  A ``bytes`` of length 1.
    """

    def __init__(self, delimiter):
        assert isinstance(delimiter, bytes)
        assert len(delimiter) == 1
        self._delimiter = delimiter

    @property
    def delimiter(self):  # pylint: disable=missing-docstring
        return self._delimiter
