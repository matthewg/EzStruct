========
EzStruct
========

:copyright: 2013 by Matthew Sachs
:license: Apache License v2.0

Expressive syntax for working with binary data formats and network
protocols.  Like the :py:mod:`struct` module, but with a more readable
syntax, especially if your format has:

* Length-prefixed variable-length byte sequences or strings
* Count-prefixed variable-count repeated fields
* Terminated (null or otherwise) strings
* String encodings
* Numbers which represent enumeration members

Example::

  tcp = ezstruct.Struct(
      "NET_ENDIAN",
      ezstruct.Field("UINT16", name="sport"),
      ezstruct.Field("UINT16", name="dport"),
      ezstruct.Field("UINT32", name="seqno"),
      ezstruct.Field("UINT32", name="ackno"),
      ezstruct.Field("UINT16",
                     name="flags",
                     value_transform=ezstruct.FieldTransform(
		         pack_flags_bitfield,
			 unpack_flags_bitfield)),
      ezstruct.Field("UINT16", name="window_size"),
      ezstruct.Field("UINT16", name="checksum"),
      ezstruct.Field("UINT16", name="urg"),
      ezstruct.Field("BYTES",
                     name="options",
		     default_pack_value={},
		     length=lambda data: data["offset"] - 5,
		     value_transform=ezstruct.FieldTransform(
                         pack_and_pad_options,
			 unpack_options)))

  header_data = {"sport": 123,
                 "dport": 456,
                 "seqno": 1,
                 "ackno": 0,
                 "flags": {"offset": 5,
		           "syn": 1},
		 "window_size": 100,
		 "checksum": 0,
		 "urg": 0}
  header_bytes = tcp.pack_bytes(header_data)
  assert tcp.unpack_bytes(header_bytes) == header_data
