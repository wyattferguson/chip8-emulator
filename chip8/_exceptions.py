class ChipException(Exception):
    """
    Base class for any Chip8 exception
    """


class FetchError(ChipException):
    pass


class DecodeError(ChipException):
    pass


class ExecuteError(ChipException):
    pass


class RomError(ChipException):
    pass


class KeypadError(ChipException):
    pass
