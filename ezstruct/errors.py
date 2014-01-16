"""Package-defined exceptions."""

class EzStructError(Exception):
    """Base class for package-defined exceptions."""
    pass


class DelimiterNotFound(EzStructError):
    """The specified delimiter :py:class:`ezstruct.Delimiter` wasn't found."""
    def __init__(self, delim):
        EzStructError.__init__(self)
        self.delim = delim

    def __str__(self):
        return "Delimiter %r not found!" % self.delim


class InconsistentLength(EzStructError):
    """A field's length function differs from the field's length."""
    def __init__(self, field, fn_len, val_len):
        EzStructError.__init__(self)
        self.field = field
        self.fn_len = fn_len
        self.val_len = val_len

    def __str__(self):
        return ("Field %s has a value of length %d, but its "
                "length function returned %d." % (self.field.name,
                                                  self.val_len,
                                                  self.fn_len))
