from dataclasses import dataclass

type Color = tuple[int, int, int]
type ScreenBuffer = list[list[int]]


@dataclass
class OpCode:
    """Chip8 OpCode."""

    label: str  # mnemonic name
    call: str  # CPU method name to call
    args: list[bool | str] | None = None  # give arguments to send to CPU method
    length: int = 2  # length of instruction in bytes
    pc_inc: bool = True  # whether to increment the program counter after execution

    def __str__(self) -> str:
        return f"{self.label} - {self.call}({self.args}) - {self.pc_inc}"
