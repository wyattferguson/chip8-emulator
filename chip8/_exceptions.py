class ChipError(Exception):
    """Base class for any Chip8 exception."""


class FetchError(ChipError):
    pass


class DecodeError(ChipError):
    pass


class ExecuteError(ChipError):
    pass


class RomError(ChipError):
    pass


class KeypadError(ChipError):
    pass
