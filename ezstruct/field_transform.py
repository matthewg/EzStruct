"""
Transforms to apply to a field's values.
"""

from __future__ import absolute_import
import collections


class FieldTransform(object):
    """A transformation to apply.

    Consists of a pair of functions, each of which is passed
    a value as its argument and must return a new value to
    use in its place.  You can use this to have a field
    whose "unpacked" value is something other than the
    literal value the packed bytes represent.

    For instance, if you have a ``UINT8`` field where the
    number actually indicates a color, you might
    have something like::

      class Color(Enum):
         red = 1
         blue = 2
         green = 3

      ...
      ezstruct.Field(
          "UINT8",
          name="color",
          value_transform=ezstruct.FieldTransform(
              lambda color: color.value,
              lambda color_num: Color(color_num))),
      ...

    Args:
      ``pack_fn``:
        A callable to invoke just after reading the value to pack,
        before doing e.g. string encoding.

      ``unpack_fn``:
        A callable to invoke just before setting the value in the
        unpack dict, after doing e.g. string decoding.
    """

    def __init__(self, pack_fn, unpack_fn):
        assert isinstance(pack_fn, collections.Callable)
        assert isinstance(unpack_fn, collections.Callable)
        self.pack = pack_fn
        self.unpack = unpack_fn
