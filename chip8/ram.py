from pathlib import Path
from typing import overload

from chip8._exceptions import RomError
from chip8.config import FONT, MEMORY_SIZE, PC_INIT


class RAM:
    """Unified memory for the CHIP-8 system."""

    def __init__(self, rom_path: str) -> None:
        self._memory: bytearray = bytearray([0] * MEMORY_SIZE)

        # Load font data into the first 80 bytes of memory
        self._memory[: len(FONT)] = FONT
        self.load_rom(rom_path)

    def load_rom(self, rom_path: str) -> None:
        """Load ROM bytes into RAM starting at 0x200."""
        try:
            with Path(rom_path).open("rb") as f:
                rom_bytes = f.read()
        except FileNotFoundError as e:
            raise RomError(f"ROM file not found: {rom_path}") from e

        if len(rom_bytes) > MEMORY_SIZE - PC_INIT:
            raise RomError("ROM size exceeds available memory.")

        # Load ROM bytes into RAM starting at 0x200.
        self._memory[PC_INIT : PC_INIT + len(rom_bytes)] = rom_bytes

    @overload
    def __getitem__(self, address: int) -> int: ...

    @overload
    def __getitem__(self, address: slice) -> list[int]: ...

    def __getitem__(self, address: int | slice) -> int | list[int]:
        """Read one byte from memory."""
        if isinstance(address, int):
            if not (0 <= address < MEMORY_SIZE):
                raise IndexError(f"Memory address out of bounds: {address:04x}")
            return self._memory[address]
        return list(self._memory[address])

    def __setitem__(self, address: int, value: int) -> None:
        """Write one byte to memory."""
        if not (0 <= address < MEMORY_SIZE):
            raise IndexError(f"Memory address out of bounds: {address:04x}")
        self._memory[address] = value

    def dump(self, start: int = 0, end: int = 0xFFFF) -> None:
        """Print memory slice in formatted rows."""
        chunk_size: int = 16
        print(f"\n################## MMU: {start:04x}-{end:04x}  ##################\n")
        for i in range(start, end + 1, chunk_size):
            chunk = self._memory[i : i + chunk_size]
            print(f"{i:04x}: " + " ".join(f"{byte:02x}" for byte in chunk))
        print("\n#####################################################\n")
