"""Top-level structure objects."""
from __future__ import absolute_import

from . import byte_order
from . import delimiter
from . import errors
from . import field

import collections
import io


class Struct(object):
    """A definition of a binary format.

    A ``Struct`` can be *packed*, converted from a dict describing the
    data to a sequence of bytes, and *unpacked*, converting from bytes
    to dict.

    Args:
      ``order``:
        Byte order for multi-byte numeric fields.  See
        :py:mod:`ezstruct.byte_order` for possible values.

      ``fields``: List of :py:class:`ezstruct.Field`.
    """

    def __init__(self, order, *fields):
        self.byte_order = byte_order.get(order)

        for the_field in fields:
            assert isinstance(the_field, field.Field)
        self.fields = fields

    def __str__(self):
        return "<EzStruct %s: [%s]>" % (self.byte_order,
                                        ", ".join([str(f)
                                                   for f in self.fields]))

    def pack_bytes(self, data):
        """Serialize ``data`` into a new ``bytes``.

        Args:
          ``data``: The data to pack.

        Returns:
          A ``bytes`` containing the packed representation of ``data``.
        """
        raw = io.BytesIO()
        buf = io.BufferedWriter(raw)
        self.pack(data, buf)
        buf.flush()
        return raw.getvalue()

    def pack(self, data, buf):
        """Serialize ``data`` into an IO buffer.

        Args:
          ``data``: The data to pack.
          ``buf``: An :py:mod:`io` buffer to write the packed data to.
        """
        for the_field in self.fields:
            vals = the_field.get_values_for_pack(data)

            if the_field.value_transform:
                vals = the_field.value_transform.pack(vals)

            if the_field.repeat == 1:
                vals = (vals, )
            elif isinstance(the_field.repeat, int):
                assert len(vals) == the_field.repeat
            else:
                the_field.repeat.pack(self.byte_order, len(vals), buf)

            for val in vals:
                if isinstance(the_field.length, field.Field):
                    the_field.length.pack(self.byte_order, len(val), buf)
                elif isinstance(the_field.length, int):
                    assert len(val) == the_field.length
                elif isinstance(the_field.length, collections.Callable):
                    fn_len = the_field.length(data)
                    val_len = len(val)
                    if fn_len != val_len:
                        raise errors.InconsistentLength(the_field,
                                                        fn_len,
                                                        val_len)

                the_field.pack(self.byte_order, val, buf)

                if isinstance(the_field.length, delimiter.Delimiter):
                    buf.write(the_field.length.delimiter)

    def unpack_bytes(self, the_bytes):
        """Unserialize data from a ``bytes``.

        Args:
          ``the_bytes``: The byte sequence to unpack.

        Returns:
          A dict containing the unpacked data.
        """
        raw = io.BytesIO(the_bytes)
        buf = io.BufferedReader(raw)
        return self.unpack(buf)

    def unpack(self, buf):
        """Unserialize data from an IO buffer.

        Args:
          ``buf``: An :py:mod:`io` buffer containing data to unpack.

        Returns:
          A dict containing the unpacked data.
        """
        assert isinstance(buf, io.BufferedIOBase)
        assert buf.readable()

        ret = {}
        for the_field in self.fields:
            vals = self._unpack_field(buf, the_field, ret)
            if the_field.name:
                ret[the_field.name] = vals
        return ret

    def _unpack_field(self, buf, the_field, unpacked_fields):
        """Unserialize data for a single field.

        Args:
          ``buf``: An :py:mod:`io` buffer.
          ``the_field``: The field to unpack.
          ``unpacked_fields``: Dictionary containing data unpacked so far.

        Returns:
          The value (or values, for repeated fields), with
          transformations applied.
        """

        repeat = the_field.repeat
        if isinstance(repeat, field.Field):
            repeat = the_field.repeat.unpack(self.byte_order, buf)

        vals = []
        for _ in range(repeat):
            val = self._unpack_field_instance(buf, the_field, unpacked_fields)
            vals.append(val)
            if isinstance(the_field.length, delimiter.Delimiter):
                buf.seek(1, io.SEEK_CUR)
        if the_field.repeat == 1:
            vals = vals[0]

        if the_field.value_transform:
            vals = the_field.value_transform.unpack(vals)

        return vals

    def _unpack_field_instance(self, buf, the_field, unpacked_fields):
        """Unserialize data for a single repetition of a field.

        Args:
          ``buf``: An :py:mod:`io` buffer.
          ``the_field``: The field to unpack.
          ``unpacked_fields``: Dictionary containing data unpacked so far.

        Returns:
          The value, *without* transformations applied.
        """

        if isinstance(the_field.length, delimiter.Delimiter):
            assert buf.seekable()
            pos = buf.tell()
            while True:
                char = buf.read(1)
                if char == b"":
                    raise errors.DelimiterNotFound(
                        the_field.length.delimiter)
                elif char == the_field.length.delimiter:
                    break
            val_len = buf.tell() - pos - 1
            buf.seek(pos, io.SEEK_SET)
        elif isinstance(the_field.length, field.Field):
            val_len = the_field.length.unpack(self.byte_order, buf)
        elif isinstance(the_field.length, int):
            val_len = the_field.length
        elif isinstance(the_field.length, collections.Callable):
            val_len = the_field.length(unpacked_fields)
        else:
            assert the_field.length is None
            val_len = None

        val = the_field.unpack(self.byte_order, buf, length=val_len)
        return val
