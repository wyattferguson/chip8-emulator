import random
from collections.abc import Callable
from operator import and_, or_, xor

from chip8._exceptions import DecodeError, ExecuteError
from chip8.config import CARRY_FLAG, CPU_CYCLES_PER_TICK, MAX_8BIT, PC_INIT, REGISTER_COUNT
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

    def __init__(self, ram: RAM, screen: Screen, keypad: Keypad) -> None:
        self.ram: RAM = ram
        self.keypad: Keypad = keypad
        self.screen: Screen = screen
        self.opcode: OpCode

        self.v: bytearray = bytearray([0] * REGISTER_COUNT)  # 16 8-Bit Registers - V0 to VF

        self.i: int = 0  # 12bit register
        self.x: int = 0  # 4-bit register
        self.y: int = 0  # 4-bit register
        self.n: int = 0  # lowest 4 bits of the instruction
        self.addr: int = 0  # lowest 12 bits of the instruction
        self.kk: int = 0  # lowest 8 bits of the instruction
        self.op_group: int = 0  # opcode group the instruction belongs to

        self.stack: list[int] = []  # Store return addresses when subroutines are called
        self.sound_timer: int = 0  # Play a beep when > 0
        self.delay_timer: int = 0

        self.pc: int = PC_INIT  # program counter, starts at 0x200 in ram

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
        self.decrement_timers()

        for _ in range(CPU_CYCLES_PER_TICK):
            self.decode()
            self.execute()
            if self.opcode.pc_inc:
                self.pc += self.opcode.length  # move pc to next instruction

    def decrement_timers(self) -> None:
        """Decrement delay and sound timers."""
        self.delay_timer -= 1 if self.delay_timer > 0 else 0
        self.sound_timer -= 1 if self.sound_timer > 0 else 0

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
        self.jmp()

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
        total = self.v[self.x] + self.v[self.y]
        self.v[CARRY_FLAG] = total >= MAX_8BIT
        self.v[self.x] = total % MAX_8BIT

    def sub_vx_vy(self) -> None:
        """Vx = Vx - Vy with underflow."""
        self._store_sub_vx_result(self.v[self.x] - self.v[self.y])

    def subn_vx_vy(self) -> None:
        """Vx = Vy - Vx with underflow."""
        self._store_sub_vx_result(self.v[self.y] - self.v[self.x])

    def _store_sub_vx_result(self, value: int) -> None:
        """Store a subtraction result in Vx and update VF."""
        self.v[CARRY_FLAG] = value >= 0
        self.v[self.x] = value % MAX_8BIT

    def shr_vx(self) -> None:
        """Set Vx = Vx SHR 1."""
        self.v[CARRY_FLAG] = self.v[self.x] & 0x1
        self.v[self.x] >>= 1

    def shl_vx(self) -> None:
        """Set Vx = Vx SHL 1."""
        self.v[CARRY_FLAG] = (self.v[self.x] & 0x80) >> 7
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
        self.v[CARRY_FLAG] = 0
        for i in range(self.n):
            sprite: int = self.ram[self.i + i]
            for j in range(8):
                if sprite & 0x80 and self.screen.flip_pixel(self.v[self.x] + j, self.v[self.y] + i):
                    self.v[CARRY_FLAG] = 1

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
        value = self.v[self.x]
        self.ram[self.i] = value // 100
        self.ram[self.i + 1] = (value // 10) % 10
        self.ram[self.i + 2] = value % 10
