"""
Values for a field's type.  Possible values:

Boolean:

  ``"BOOL"``
    A one-byte type; ``\\x00`` unpacks to ``False``, all
    other values unpack to ``True``.

Bytes:

  ``"BYTES"``
    A sequence of raw bytes.  Fields of this type must
    have ``length`` specified.

Integers:

  ``"SINT8"``
    8 bits, signed.

  ``"SINT16"``
    16 bits, signed.

  ``"SINT32"``
    32 bits, signed.

  ``"SINT64"``
    64 bits, signed.

  ``"UINT8"``
    8 bits, unsigned.

  ``"UINT16"``
    16 bits, unsigned.

  ``"UINT32"``
    32 bits, unsigned.

  ``"UINT64"``
    64 bits, unsigned.

Floating-Point Numbers:

  ``"FLOAT"``
    4 bytes in IEEE 754 binary32 format.

  ``"DOUBLE"``
    8 bytes in IEEE 754 binary64 format.

Strings:

  ``"STRING"``
    A string.  Fields of this type must have
    both ``length`` and ``string_encoding`` specified.
"""
from __future__ import absolute_import

import six


class _FieldType(object):
    """Abstract base class for field types."""
    _unpacked_type = None
    _variable_length = False

    def __init__(self, names, pack_char):
        assert self.__class__.unpacked_type
        self._names = names
        self._pack_char = pack_char

    def __str__(self):
        return self._names[0]

    @property
    def pack_char(self):
        """The character used for this type in :py:mod:`struct` syntax."""
        return self._pack_char

    @property
    def unpacked_type(self):
        """The Python datatype this field type unpacks into."""
        return self._unpacked_type

    @property
    def variable_length(self):
        """Can the number of bytes this takes when packed vary?"""
        return self._variable_length


class _BoolFieldType(_FieldType):
    """Boolean values."""
    _unpacked_type = bool


class _BytesFieldType(_FieldType):
    """Raw bytes."""
    if six.PY2:  # pragma: no cover
        _unpacked_type = str
    else:
        _unpacked_type = bytes
    variable_length = True


class _IntFieldType(_FieldType):
    """Integers."""
    _unpacked_type = int


class _FloatFieldType(_FieldType):
    """Floating-point numbers."""
    _unpacked_type = float


class _StringFieldType(_FieldType):
    """Strings (ASCII, Unicode, etc.)"""
    if six.PY2:  # pragma: no cover
        _unpacked_type = unicode  # pylint: disable=undefined-variable
    else:
        _unpacked_type = str
    require_string_encoding = True
    variable_length = True


_FIELD_TYPES = {}


def _register_field_type(type_class, names, pack_char):
    the_type = type_class(names, pack_char)
    for name in names:
        _FIELD_TYPES[name] = the_type


_register_field_type(_BoolFieldType, ("BOOL",), "?")
_register_field_type(_BytesFieldType, ("BYTES",), "s")
_register_field_type(_FloatFieldType, ("DOUBLE",), "d")
_register_field_type(_FloatFieldType, ("FLOAT",), "f")
_register_field_type(_IntFieldType, ("SINT8",), "b")
_register_field_type(_IntFieldType, ("SINT16",), "h")
_register_field_type(_IntFieldType, ("SINT32",), "l")
_register_field_type(_IntFieldType, ("SINT64",), "q")
_register_field_type(_IntFieldType, ("UINT8",), "B")
_register_field_type(_IntFieldType, ("UINT16",), "H")
_register_field_type(_IntFieldType, ("UINT32",), "L")
_register_field_type(_IntFieldType, ("UINT64",), "Q")
_register_field_type(_StringFieldType, ("STRING",), "s")


def get(name):  # pylint: disable=missing-docstring
    return _FIELD_TYPES[name]
