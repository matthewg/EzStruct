import ezstruct
import ezstruct.errors
import six
import sys
import unicodedata
import unittest

class EzStructTest(unittest.TestCase):

    if six.PY2:
        assertRaisesRegex = unittest.TestCase.assertRaisesRegexp

    def roundTrip(self, ezs, packed, unpacked):
        self.assertEqual(packed, ezs.pack_bytes(unpacked))
        self.assertEqual(unpacked, ezs.unpack_bytes(packed))

    def test_str(self):
        ezs = ezstruct.Struct("NET_ENDIAN",
                              ezstruct.Field("UINT8"),
                              ezstruct.Field("BOOL", name="x"))
        self.assertEqual("<EzStruct BIG_ENDIAN: [UINT8, x=BOOL]>",
                         str(ezs))

    def test_endian(self):
        fields = [ezstruct.Field("UINT16", name="a")]
        native_endian = ezstruct.Struct("NATIVE_ENDIAN",
                                        *fields)
        big_endian = ezstruct.Struct("BIG_ENDIAN", *fields)
        little_endian = ezstruct.Struct("LITTLE_ENDIAN", *fields)
        net_endian = ezstruct.Struct("NET_ENDIAN", *fields)

        data = {"a": 0x1234}

        if sys.byteorder == "little":
            expect_native = b"\x34\x12"
        else:
            expect_native = b"\x12\x34"
        expect_big = b"\x12\x34"
        expect_little = b"\x34\x12"
        expect_net = expect_big

        self.roundTrip(native_endian, expect_native, data)
        self.roundTrip(big_endian, expect_big, data)
        self.roundTrip(little_endian, expect_little, data)
        self.roundTrip(net_endian, expect_net, data)

    def test_nums(self):
        ezs = ezstruct.Struct("NET_ENDIAN",
                              ezstruct.Field("SINT8", name="a"),
                              ezstruct.Field("UINT8", name="b"),
                              ezstruct.Field("SINT16", name="c"),
                              ezstruct.Field("UINT16", name="d"),
                              ezstruct.Field("SINT32", name="e"),
                              ezstruct.Field("UINT32", name="f"),
                              ezstruct.Field("SINT32", name="g"),
                              ezstruct.Field("UINT32", name="h"),
                              ezstruct.Field("SINT64", name="i"),
                              ezstruct.Field("UINT64", name="j"))

        unpacked = {"a": 0x0A,
                    "b": 0xFE,
                    "c": 0x0400,
                    "d": 0x03E7,
                    "e": 0x00000F00,
                    "f": 0x0000BEEF,
                    "g": 0x00BADCAB,
                    "h": 0xFEEDFACE,
                    "i": -1,
                    "j": 1}
        packed = (b"\x0A"
                  b"\xFE"
                  b"\x04\x00"
                  b"\x03\xE7"
                  b"\x00\x00\x0F\x00"
                  b"\x00\x00\xBE\xEF"
                  b"\x00\xBA\xDC\xAB"
                  b"\xFE\xED\xFA\xCE"
                  b"\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF"
                  b"\x00\x00\x00\x00\x00\x00\x00\x01")
        self.roundTrip(ezs, packed, unpacked)
 
    def test_length(self):
        ezs = ezstruct.Struct("NET_ENDIAN",
                              ezstruct.Field("BYTES", name="a", length=5),
                              ezstruct.Field("BYTES", name="b", length=ezstruct.Field("UINT8")))
        self.roundTrip(ezs, b"12345\x00", {"a": b"12345", "b": b""})
        self.roundTrip(ezs, b"12345\x01x", {"a": b"12345", "b": b"x"})
        self.roundTrip(ezs, b"12345\x03xxx", {"a": b"12345", "b": b"xxx"})

    def test_repeat(self):
        ezs = ezstruct.Struct("NET_ENDIAN",
                              ezstruct.Field("UINT8", name="a", repeat=3),
                              ezstruct.Field("UINT8", name="b", repeat=ezstruct.Field("UINT8")),
                              ezstruct.Field("BYTES", name="c", length=ezstruct.Field("UINT8"),
                                             repeat=ezstruct.Field("UINT8")))
        self.roundTrip(ezs,
                       (b"\x00\x01\x02"
                        b"\x00"
                        b"\x00"),
                       {"a": [0, 1, 2],
                        "b": [],
                        "c": []})
        self.roundTrip(ezs,
                       (b"\x00\x01\x02"
                        b"\x00"
                        b"\x02\x00\x00"),
                       {"a": [0, 1, 2],
                        "b": [],
                        "c": [b"", b""]})
        self.roundTrip(ezs,
                       (b"\x09\x0A\x0B"
                        b"\x05\x03\x01\x04\x01\x06"
                        b"\x03\x01a\x02xy\x03cat"),
                       {"a": [9, 10, 11],
                        "b": [3, 1, 4, 1, 6],
                        "c": [b"a", b"xy", b"cat"]})

    def test_delimiter(self):
        ezs = ezstruct.Struct("NET_ENDIAN",
                              ezstruct.Field("BYTES", name="a", length=ezstruct.Delimiter(b"\x00")),
                              ezstruct.Field("BYTES", name="b", length=1))
        self.roundTrip(ezs, b"abc\x00d", {"a": b"abc", "b": b"d"})
        self.assertRaisesRegex(ezstruct.errors.DelimiterNotFound,
                               r"""Delimiter b?'\\x00' not found!""",
                               ezs.unpack_bytes, b"xyz")

    def test_default_pack_value(self):
        ezs = ezstruct.Struct("NET_ENDIAN",
                              ezstruct.Field("UINT8", default_pack_value=0),
                              ezstruct.Field("UINT8", default_pack_value=1),
                              ezstruct.Field("UINT8", name="a", default_pack_value=2),
                              ezstruct.Field("UINT8", repeat=2, default_pack_value=[3, 4]))
        self.assertEqual({"a": 0xAA}, ezs.unpack_bytes(b"\xFF\xFF\xAA\xBB\xCC"))
        self.assertEqual(b"\x00\x01\x02\x03\x04", ezs.pack_bytes({}))
        self.assertEqual(b"\x00\x01\xAA\x03\x04", ezs.pack_bytes({"a": 0xAA}))

    def test_string_encoding(self):
        ezs = ezstruct.Struct("NET_ENDIAN",
                              ezstruct.Field("STRING",
                                             string_encoding="ascii",
                                             name="ascii",
                                             length=ezstruct.Delimiter(b"\xFF")),
                              ezstruct.Field("STRING",
                                             string_encoding="utf-8",
                                             name="utf-8",
                                             length=ezstruct.Delimiter(b"\xFF")),
                              ezstruct.Field("STRING",
                                             string_encoding="utf-16-le",
                                             name="utf-16-le",
                                             length=ezstruct.Delimiter(b"\xFF")))
        self.roundTrip(ezs,
                       b"cat\xFFdog\xFFf\x00o\x00x\x00\xFF",
                       {"ascii": "cat", "utf-8": "dog", "utf-16-le": "fox"})
        self.roundTrip(ezs,
                       b"meow\xFFw\xC3\xB6\xC3\xB6f\xFF\x34\xD8\x1E\xDD\xFF",
                       {"ascii": "meow",
                        "utf-8": u"w\u00F6\u00F6f",
                        "utf-16-le": unicodedata.lookup(
                            "MUSICAL SYMBOL G CLEF")})

        ezs = ezstruct.Struct("NET_ENDIAN",
                              ezstruct.Field("STRING", string_encoding="ascii",
                                             length=1, name="a"),
                              ezstruct.Field("STRING", string_encoding="ascii",
                                             length=1, name="b",
                                             string_encoding_errors_policy="backslashreplace"))
        self.assertRaisesRegex(ValueError,
                               (r"""'ascii' codec can't encode character u?'\\xf6' """
                                r"""in position 0: ordinal not in range\(128\)"""),
                               ezs.pack_bytes, {"a": u"\u00F6", "b": "x"})
        self.assertEqual(b"x\\xf6", ezs.pack_bytes({"a": "x", "b": u"\u00F6"}))

    def test_value_transform(self):
        # repeat=1
        # repeat=multiple
        # length=variable
        transformed_values = [b"zero", b"one", b"two"]
        elt_to_idx = transformed_values.index
        idx_to_elt = lambda idx: transformed_values[idx]
        ezs = ezstruct.Struct(
            "NET_ENDIAN",
            ezstruct.Field("UINT8", name="a",
                           value_transform=ezstruct.FieldTransform(elt_to_idx,
                                                                   idx_to_elt)),
            # Test interaction of repeats and transform:
            # Transform gets called w/ list of values.
            ezstruct.Field("UINT8", name="b", repeat=3,
                           value_transform=ezstruct.FieldTransform(
                               lambda elts: [elt_to_idx(e) for e in elts],
                               lambda idxs: [idx_to_elt(i) for i in idxs])),
            # Test interaction of length-prefix and transform:
            # Length is length of transformed value.
            ezstruct.Field("BYTES",
                           name="c",
                           repeat=3,
                           length=ezstruct.Field("UINT8"),
                           value_transform=ezstruct.FieldTransform(
                               lambda idxs: [idx_to_elt(i) for i in idxs],
                               lambda elts: [elt_to_idx(e) for e in elts])))
        self.roundTrip(ezs,
                       b"\x01\x02\x00\x01\x03one\x03two\x04zero",
                       {"a": b"one",
                        "b": [b"two", b"zero", b"one"],
                        "c": [1, 2, 0]})

    def test_length_function(self):
        ezs = ezstruct.Struct(
            "NET_ENDIAN",
            ezstruct.Field("UINT8", name="foo_len"),
            ezstruct.Field("UINT8", default_pack_value=0),
            ezstruct.Field("BYTES",
                           name="foo",
                           length=lambda data: data["foo_len"]))
        self.roundTrip(ezs, b"\x00\x00", {"foo_len": 0, "foo": b""})
        self.roundTrip(ezs,
                       b"\x05\x00abcde",
                       {"foo_len": 5,
                        "foo": b"abcde"})
        self.assertRaisesRegex(ezstruct.errors.InconsistentLength,
                               ("Field foo has a value of length 3, "
                                "but its length function returned 5."),
                               ezs.pack_bytes,
                               {"foo_len": 5,
                                "foo": b"abc"})


if __name__ == "__main__":
    unittest.main()
