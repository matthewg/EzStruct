"""Fields within a structure."""
from __future__ import absolute_import

from . import delimiter
from . import field_transform
from . import field_type

import codecs
import collections
import six
import struct


if six.PY2:  # pragma: no cover
    _StringClass = unicode  # pylint: disable=undefined-variable, invalid-name
else:
    _StringClass = str


class Field(object):  # pylint: disable=too-many-instance-attributes
    """A value within a :py:class:`ezstruct.Struct`.

    Args:
      ``ft``:
        The field type.  See :py:mod:`ezstruct.field_type` for possible values.

      ``name``:
        The key to use for the field value in the dictionary used to
        represent an unpacked version of the structure.  If ``None``,
        the value will not be represented in the dict.

      ``repeat``:

        If non-None, the packed structure contains multiple instances
        of the field, one after the other.  This can be:

        * An ``int``, if there are a fixed number of repetitions; or,
        * A ``Field`` if there are a value number; e.g., if the packed
          structure contains an 8-byte value indicating the number of
          copies of this field that follow.  For variable repeats, or
          fixed repeats > 1, the data in the packed structure will be
          a list containing the value from each repetition.

      ``default_pack_value``:
        If non-``None``, the specified value will be used when packing
        this field if the input to the pack function doesn't contain
        this field.

      ``string_encoding``:
        For string fields, the encoding (as per :py:mod:`codecs`) to use for
        the string.

      ``string_encoding_errors_policy``: See :py:mod:`codecs`.

      ``length``:
        For variable-length fields (``"STRING"`` and ``"BYTES"``), the
        length of the field.  This can be:

        * An ``int``, for fixed-length fields;
        * A ``Field``, for variable-length fields, e.g., if the packed
          structure contains an 8-byte value indicating the length of
          the string that follows.
        * A :py:class:`ezstruct.Delimiter`, for fields
          whose end is indicated by a specific byte; or,
        * A function that takes a single argument, a dictionary of the
          structure's unpacked data.  You can use this for fields
          whose length is determined by the value of a prior field.
          When packing, the function is called with the dictionary
          given to the ``pack`` function, and if the field's length
          doesn't match the value returned by the function,
          ``InconsistentLength`` is raised.  When unpacking, the
          function is called with a dictionary containing the data
          unpacked so far.

      ``value_transform``: See :py:class:`ezstruct.FieldTransform`.
    """

    # pylint: disable=too-many-arguments
    def __init__(self, ft,
                 name=None,
                 repeat=None,
                 default_pack_value=None,
                 string_encoding=None,
                 string_encoding_errors_policy="strict",
                 length=None,
                 value_transform=None):
        self._type = field_type.get(ft)

        assert isinstance(name, (type(None), str))
        self._name = name

        if repeat is not None:
            assert isinstance(repeat, (int, Field))
            if isinstance(repeat, Field):
                assert repeat.type.unpacked_type is int
                assert repeat.repeat == 1
            else:
                assert repeat > 0
        self._repeat = repeat or 1

        if default_pack_value is not None:
            if self._repeat > 1:
                assert isinstance(default_pack_value, collections.Iterable)
        self._default_pack_value = default_pack_value

        if self._type.unpacked_type is _StringClass:
            assert string_encoding is not None
            # Raises exception if encoding not found.
            codecs.lookup(string_encoding)
        else:
            assert string_encoding is None
        self._string_encoding = string_encoding
        self._string_encoding_errors_policy = string_encoding_errors_policy

        if length is not None:
            assert self._type.variable_length
            assert isinstance(length,
                              (int,
                               delimiter.Delimiter,
                               Field,
                               collections.Callable))
            if isinstance(length, int):
                assert length > 0
            elif isinstance(length, Field):
                assert length.type.unpacked_type is int
        self._length = length

        assert isinstance(value_transform,
                          (field_transform.FieldTransform, type(None)))
        self._value_transform = value_transform

    def __str__(self):
        name = ""
        if self.name:
            name = "%s=" % self.name
        return "%s%s" % (name, str(self._type))

    @property
    def length(self):  # pylint: disable=missing-docstring
        return self._length

    @property
    def name(self):  # pylint: disable=missing-docstring
        return self._name

    @property
    def type(self):  # pylint: disable=missing-docstring
        return self._type

    @property
    def repeat(self):  # pylint: disable=missing-docstring
        return self._repeat

    @property
    def value_transform(self):  # pylint: disable=missing-docstring
        return self._value_transform

    def get_values_for_pack(self, data):
        """Retrieves the value to pack for this field from the unpacked form."""
        if self.name:
            return data.get(self.name, self._default_pack_value)
        else:
            return self._default_pack_value

    def pack(self, byte_order, val, buf):
        """Serialize the field.

        Args:
          ``byte_order``: The ``ByteOrder`` of the enclosing structure.
          ``val``: The value to serialize.
          ``buf``: The :py:mod:`io` buffer to write the serialized data to.
        """
        if self._string_encoding:
            val = codecs.encode(val,
                                self._string_encoding,
                                self._string_encoding_errors_policy)

        if self._type.variable_length:
            fmt = "%s%d%s" % (byte_order.pack_char,
                              len(val),
                              self._type.pack_char)
        else:
            fmt = "%s%s" % (byte_order.pack_char, self._type.pack_char)
        buf.write(struct.pack(fmt, val))

    def unpack(self, byte_order, buf, length=None):
        """Deserialize the field.

        Args:

          ``byte_order``: The ``ByteOrder`` of the enclosing structure.

          ``buf``: The :py:mod:`io` buffer to read serialized data from.

          ``length``:
            If the field's length can vary, the number of bytes
            of data to deserialize.

        Returns:
          The parsed value.
        """

        if length is None:
            fmt = "%s%s" % (byte_order.pack_char, self._type.pack_char)
            length = struct.calcsize(fmt)
        else:
            fmt = "%s%d%s" % (byte_order.pack_char,
                              length,
                              self._type.pack_char)

        data = buf.read(length)
        ret = struct.unpack(fmt, data)[0]
        if self._string_encoding:
            ret = codecs.decode(ret,
                                self._string_encoding,
                                self._string_encoding_errors_policy)
        return ret
