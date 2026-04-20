import random
from collections.abc import Callable
from operator import and_, or_, xor

from chip8._exceptions import DecodeError, ExecuteError
from chip8.config import CPU_CYCLES_PER_TICK, MAX_8BIT, PC_INIT, REGISTER_COUNT
from chip8.ctypes import OpCode
from chip8.keypad import Keypad
from chip8.opcodes import opcodes
from chip8.ram import RAM
from chip8.screen import Screen

BITWISE_OPERATORS: dict[str, Callable[[int, int], int]] = {
    "|": or_,
    "&": and_,
    "^": xor,
}


class CPU:
    """Chip8 CPU."""

    v: bytearray = bytearray([0] * REGISTER_COUNT)  # 16 8-Bit Registers - V0 to VF

    i: int = 0  # 12bit register
    x: int = 0  # 4-bit register
    y: int = 0  # 4-bit register
    n: int = 0  # lowest 4 bits of the instruction
    addr: int = 0  # lowest 12 bits of the instruction
    kk: int = 0  # lowest 8 bits of the instruction
    op_group: int = 0  # opcode group the instruction belongs to

    stack: list[int] = []  # Store return addresses when subroutines are called  # noqa: RUF012
    sound_timer: int = 0  # Play a beep when > 0
    delay_timer: int = 0

    pc: int = PC_INIT  # program counter, starts at 0x200 in ram

    def __init__(self, ram: RAM, screen: Screen, keypad: Keypad) -> None:
        self.ram: RAM = ram
        self.keypad: Keypad = keypad
        self.screen: Screen = screen
        self.opcode: OpCode | None = None

    def decode(self) -> None:
        """Retreive and decode next opcode."""
        try:
            # Every opcode is 2 bytes long, shift the first 8 bits left
            # Combine it with the next 8 bits to make a full opcode
            instruction = (self.ram[self.pc] << 8) | self.ram[self.pc + 1]
            self.x = (instruction & 0x0F00) >> 8  # lower 4 bits of the high byte
            self.y = (instruction & 0x00F0) >> 4  # upper 4 bits of the low byte
            self.n = instruction & 0x000F  # lowest 4 bits of the low byte
            self.addr = instruction & 0x0FFF  # lowest 12 bits
            self.kk = instruction & 0x00FF  # lowest 8 bits
            self.opcode = self.opcode_lookup(instruction)
        except Exception as e:
            raise DecodeError(f"Unable to decode opcode: {instruction} - {e}") from e

    def execute(self) -> None:
        """Execute current opcode."""
        try:
            if self.opcode.args is None:
                getattr(self, self.opcode.call)()
            else:
                getattr(self, self.opcode.call)(*self.opcode.args)
        except Exception as e:
            raise ExecuteError(
                f"Execution Error: {self.opcode} - {e}",
            ) from e

    def opcode_lookup(self, instruction: int) -> OpCode:
        """Convert instruction into an opcode."""
        op_index = instruction & 0xF000
        if op_index in [0xE000, 0xF000, 0x0]:
            op_index = instruction & 0xF0FF
        elif op_index == 0x8000:
            op_index = instruction & 0xF00F
        return opcodes[op_index]

    def cycle(self) -> None:
        """Next CPU instruction."""
        if self.delay_timer > 0:
            self.delay_timer -= 1

        if self.sound_timer > 0:
            self.sound_timer -= 1

        for _ in range(CPU_CYCLES_PER_TICK):
            self.decode()
            self.execute()
            if self.opcode.pc_inc:
                self.pc += self.opcode.length  # move pc to next instruction

    def cls(self) -> None:
        """Clear screen."""
        self.screen.clear()

    def ret(self) -> None:
        """Return from subroutine."""
        self.pc = self.stack.pop()

    def jmp(self) -> None:
        """Jump to address."""
        self.pc = self.addr

    def sub(self) -> None:
        """Call subroutine."""
        self.stack.append(self.pc)
        self.pc = self.addr

    def se_vx(self) -> None:
        """Skip next instruction if Vx == kk."""
        if self.v[self.x] == self.kk:
            self.pc += self.opcode.length

    def sne_vx(self) -> None:
        """Skip next instruction if Vx != kk."""
        if self.v[self.x] != self.kk:
            self.pc += self.opcode.length

    def se_vx_vy(self) -> None:
        """Skip next instruction if Vx == Vy."""
        if self.v[self.x] == self.v[self.y]:
            self.pc += self.opcode.length

    def load_vx(self) -> None:
        """Set Vx = kk."""
        self.v[self.x] = self.kk

    def add_vx_kk(self) -> None:
        """Set Vx = Vx + kk."""
        self.v[self.x] = (self.v[self.x] + self.kk) % MAX_8BIT

    def set_vx_vy(self) -> None:
        """Set Vx = Vy."""
        self.v[self.x] = self.v[self.y]

    def bitwise_vx_vy(self, operator_symbol: str) -> None:
        """Apply a bitwise operation between Vx and Vy and store in Vx."""
        try:
            operation = BITWISE_OPERATORS[operator_symbol]
        except KeyError as e:
            raise ValueError(f"Unsupported bitwise operator: {operator_symbol}") from e

        self.v[self.x] = operation(self.v[self.x], self.v[self.y])

    def add_vx_vy(self) -> None:
        """Vx = Vx + Vy with carry."""
        v_sum: int = self.v[self.x] + self.v[self.y]
        self.v[0xF] = 1 if v_sum > MAX_8BIT - 1 else 0  # set carry flag
        self.v[self.x] = v_sum % MAX_8BIT

    def sub_vx_vy(self) -> None:
        """Vx = Vx - Vy with underflow."""
        v_diff: int = self.v[self.x] - self.v[self.y]
        self.v[0xF] = 1 if self.v[self.x] >= self.v[self.y] else 0  # set not-borrow flag
        self.v[self.x] = v_diff % MAX_8BIT

    def subn_vx_vy(self) -> None:
        """Vx = Vy - Vx with underflow."""
        v_diff: int = self.v[self.y] - self.v[self.x]
        self.v[0xF] = 1 if self.v[self.y] >= self.v[self.x] else 0  # set not-borrow flag
        self.v[self.x] = v_diff % MAX_8BIT

    def shr_vx(self) -> None:
        """Set Vx = Vx SHR 1."""
        self.v[0xF] = self.v[self.x] & 0x1
        self.v[self.x] >>= 1

    def shl_vx(self) -> None:
        """Set Vx = Vx SHL 1."""
        self.v[0xF] = (self.v[self.x] & 0x80) >> 7
        self.v[self.x] = (self.v[self.x] << 1) % MAX_8BIT

    def sne_vx_vy(self) -> None:
        """Skip next instruction if Vx != Vy."""
        if self.v[self.x] != self.v[self.y]:
            self.pc += self.opcode.length

    def load_i(self) -> None:
        """Set I = addr."""
        self.i = self.addr

    def jmp_v0_addr(self) -> None:
        """Jump to location addr + V0."""
        self.pc = self.addr + self.v[0]

    def rnd(self) -> None:
        """Set Vx = random byte AND kk."""
        self.v[self.x] = random.randint(0, MAX_8BIT - 1) & self.kk

    def draw(self) -> None:
        """Display n-byte sprite starting at memory location I at (Vx, Vy), set VF = collision."""
        self.v[0xF] = 0
        for i in range(self.n):
            sprite: int = self.ram[self.i + i]
            for j in range(8):
                if sprite & 0x80 and self.screen.flip_pixel(self.v[self.x] + j, self.v[self.y] + i):
                    self.v[0xF] = 1

                sprite <<= 1

    def skp_vx(self, equal: bool) -> None:
        """Skip next instruction if key with the value of Vx is pressed/not pressed."""
        if self.keypad.pressed_keys[self.v[self.x] & 0xF] == equal:
            self.pc += self.opcode.length

    def wait(self) -> None:
        """Wait for a key press, store the value of the key in Vx."""
        if not any(self.keypad.pressed_keys):
            self.pc -= self.opcode.length  # rewind program counter to repeat this instruction
            return

        self.v[self.x] = self.keypad.pressed_keys.index(True)

    def load_dt_vx(self) -> None:
        """Set delay timer = Vx."""
        self.delay_timer = self.v[self.x]

    def load_st_vx(self) -> None:
        """Set sound timer = Vx."""
        self.sound_timer = self.v[self.x]

    def load_vx_dt(self) -> None:
        """Set Vx = delay timer."""
        self.v[self.x] = self.delay_timer

    def add_i_vx(self) -> None:
        """Set I = I + Vx."""
        self.i += self.v[self.x]

    def load_vx_i(self) -> None:
        """Read registers V0 through Vx from memory starting at location I."""
        for i in range(self.x + 1):
            self.v[i] = self.ram[self.i + i]

    def load_f_vx(self) -> None:
        """Set I = location of sprite for digit Vx."""
        self.i = self.v[self.x] * 5

    def load_i_vx(self) -> None:
        """Store registers V0 through Vx in memory starting at location I."""
        for i in range(self.x + 1):
            self.ram[self.i + i] = self.v[i]

    def load_bcd(self) -> None:
        """Store BCD representation of Vx in memory locations I, I+1, and I+2."""
        bcd_value = f"{self.v[self.x]:03d}"
        for n in range(3):
            self.ram[self.i + n] = int(bcd_value[n])
