"""
Values for a structure's byte ordering.  Possible values:

``"NATIVE_ENDIAN"``
  Host byte ordering.

``"LITTLE_ENDIAN"``
  Little-endian, e.g. the 2-byte number ``"\\x00\\x01"`` is ``1``.

``"BIG_ENDIAN"``
  Big-endian, e.g. the 2-byte number ``"\\x01\\x00"`` is ``1``.

``"NET_ENDIAN"``
  Network byte order, i.e. big-endian.
"""

class _ByteOrder(object):
    """Order of bytes within a multi-byte number."""

    def __init__(self, names, pack_char):
        self._names = names
        self._pack_char = pack_char

    def __str__(self):
        return self._names[0]

    @property
    def pack_char(self):
        """The character used for this type in :py:mod:`struct` syntax."""
        return self._pack_char


_BYTE_ORDERS = {}


def _register_byte_order(names, *args, **kwargs):
    order = _ByteOrder(names, *args, **kwargs)
    for name in names:
        _BYTE_ORDERS[name] = order


_register_byte_order(("NATIVE_ENDIAN",), "=")
_register_byte_order(("LITTLE_ENDIAN",), "<")
_register_byte_order(("BIG_ENDIAN", "NET_ENDIAN"), ">")


def get(name):  # pylint: disable=missing-docstring
    return _BYTE_ORDERS[name]
