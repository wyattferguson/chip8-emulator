from dataclasses import dataclass, field

type Color = tuple[int, int, int]
type ScreenBuffer = list[list[int]]


@dataclass(frozen=True)
class OpCode:
    """Chip8 OpCode."""

    label: str  # mnemonic name
    call: str  # CPU method name to call
    args: list[bool | str] = field(default_factory=list)  # args to pass to call
    length: int = 2  # length of instruction in bytes
    pc_inc: bool = True  # increment the program counter after execution

    def __str__(self) -> str:
        return f"{self.label} - {self.call}({self.args}) - {self.pc_inc}"
