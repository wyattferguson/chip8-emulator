import random

from chip8._config import FONT, MEMORY_SIZE, REGISTERS_COUNT
from chip8._exceptions import DecodeError, ExecuteError, RomError
from chip8.keypad import Keypad
from chip8.opcodes import OpCode, opcodes
from chip8.screen import Screen


class CPU:
    """Chip8 CPU."""

    ram: bytearray = bytearray([0] * MEMORY_SIZE)  # 4kb of memory
    v: bytearray = bytearray([0] * REGISTERS_COUNT)  # 16 8-Bit Registers - V0 to VF

    i: int = 0  # 12bit register
    x: int = 0  # 4-bit register
    y: int = 0  # 4-bit register
    n: int = 0  # lowest 4 bits of the instruction
    addr: int = 0  # lowest 12 bits of the instruction
    kk: int = 0  # lowest 8 bits of the instruction
    op_group: int = 0  # opcode group the instruction belongs to

    cur_inst: OpCode | None = None  # current instruction being run
    stack: list[int] = []  # Store return addresses when subroutines are called
    sound_timer: int = 0  # Play a beep when > 0
    delay_timer: int = 0

    pc: int = 0x200  # program counter, starts at 0x200 in ram

    def __init__(self, rom: str, screen: Screen, keypad: Keypad) -> None:
        self.keypad: Keypad = keypad
        self.screen: Screen = screen
        self.ram[0 : len(FONT)] = FONT  # load font into memory
        self.load_rom(rom)
        self.opcode: int = 0

    def load_rom(self, rom: str) -> None:
        """Copy ROM into memory."""
        try:
            with open(rom, "rb") as rom_ptr:
                rom_data: bytes = rom_ptr.read()
                self.ram[self.pc : self.pc + len(rom_data)] = bytearray(rom_data)
        except Exception as e:
            raise RomError(f"Unable to load ROM: {rom} - {e}") from e

    def decode(self) -> None:
        """Retreive and decode next opcode."""
        try:
            # Every opcode is 2 bytes long, shift the first 8 bits left
            # Combine it with the next 8 bits to make a full opcode
            self.opcode = (self.ram[self.pc] << 8) | self.ram[self.pc + 1]
            self.x = (self.opcode & 0x0F00) >> 8  # lower 4 bits of the high byte
            self.y = (self.opcode & 0x00F0) >> 4  # upper 4 bits of the low byte
            self.n = self.opcode & 0x000F  # lowest 4 bits of the low byte
            self.addr = self.opcode & 0x0FFF  # lowest 12 bits
            self.kk = self.opcode & 0x00FF  # lowest 8 bits
            self.op_group = self.opcode & 0xF000
        except Exception as e:
            raise DecodeError(f"Unable to decode opcode: {self.opcode} - {e}") from e

    def execute(self) -> None:
        """Execute current opcode."""
        try:
            if self.op_group in [0xE000, 0xF000, 0x0]:
                self.op_group = self.opcode & 0xF0FF
            elif self.op_group == 0x8000:
                self.op_group = self.opcode & 0xF00F
            self.cur_inst = opcodes[self.op_group]
            if self.cur_inst.args:
                getattr(self, self.cur_inst.call)(*self.cur_inst.args)
            else:
                getattr(self, self.cur_inst.call)()
        except Exception as e:
            raise ExecuteError(
                f"Execution Error: {self.opcode} / {self.op_group} / {self.cur_inst} - {e}",
            ) from e

    def cycle(self) -> None:
        """Next CPU instruction."""
        if self.delay_timer > 0:
            self.delay_timer -= 1

        if self.sound_timer > 0:
            self.sound_timer -= 1

        for _ in range(5):
            self.decode()
            self.execute()
            self.pc += 2  # move program counter up 2 bytes to next instruction

    def cls(self) -> None:
        """Clear screen."""
        self.screen.clear()

    def ret(self) -> None:
        """Return from subroutine."""
        self.pc = self.stack.pop()

    def jmp(self) -> None:
        """Jump to address."""
        self.pc = self.addr - 2

    def sub(self) -> None:
        """Call subroutine."""
        self.stack.append(self.pc)
        self.pc = self.addr - 2

    def se_vx(self) -> None:
        """Skip next instruction if Vx == kk."""
        if self.v[self.x] == self.kk:
            self.pc += 2

    def sne_vx(self) -> None:
        """Skip next instruction if Vx != kk."""
        if self.v[self.x] != self.kk:
            self.pc += 2

    def se_vx_vy(self) -> None:
        """Skip next instruction if Vx == Vy."""
        if self.v[self.x] == self.v[self.y]:
            self.pc += 2

    def load_vx(self) -> None:
        """Set Vx = kk."""
        self.v[self.x] = self.kk

    def add_vx_kk(self) -> None:
        """Set Vx = Vx + kk."""
        self.v[self.x] = (self.v[self.x] + self.kk) % 256

    def set_vx_vy(self) -> None:
        """Set Vx = Vy."""
        self.v[self.x] = self.v[self.y]

    def or_vx_vy(self) -> None:
        """Set Vx = Vx OR Vy."""
        self.v[self.x] |= self.v[self.y]

    def and_vx_vy(self) -> None:
        """Set Vx = Vx AND Vy."""
        self.v[self.x] &= self.v[self.y]

    def xor_vx_vy(self) -> None:
        """Set Vx = Vx XOR Vy."""
        self.v[self.x] ^= self.v[self.y]

    def add_vx_vy(self) -> None:
        """Vx = Vx + Vy with carry."""
        v_sum: int = self.v[self.x] + self.v[self.y]
        self.v[0xF] = 1 if v_sum > 255 else 0  # set carry flag
        self.v[self.x] = v_sum % 256

    def sub_vx_vy(self) -> None:
        """Vx = Vx - Vy with underflow."""
        v_diff: int = self.v[self.x] - self.v[self.y]
        self.v[0xF] = 1 if v_diff > 0 else 0  # set underflow flag
        self.v[self.x] = v_diff % 256

    def subn_vx_vy(self) -> None:
        """Vx = Vy - Vx with underflow."""
        v_diff: int = self.v[self.y] - self.v[self.x]
        self.v[0xF] = 1 if v_diff > 0 else 0  # set underflow flag
        self.v[self.x] = v_diff % 256

    def shr_vx(self) -> None:
        """Set Vx = Vx SHR 1."""
        self.v[0xF] = self.v[self.x] & 0x1
        self.v[self.x] >>= 1

    def shl_vx(self) -> None:
        """Set Vx = Vx SHL 1."""
        self.v[0xF] = self.v[self.x] & 0x1
        self.v[self.x] <<= 1

    def sne_vx_vy(self) -> None:
        """Skip next instruction if Vx != Vy."""
        if self.v[self.x] != self.v[self.y]:
            self.pc += 2

    def load_i(self) -> None:
        """Set I = addr."""
        self.i = self.addr

    def jmp_v0_addr(self) -> None:
        """Jump to location addr + V0."""
        self.pc = self.addr + self.v[0]

    def rnd(self) -> None:
        """Set Vx = random byte AND kk."""
        self.v[self.x] = random.randint(0, 255) & self.kk

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
            self.pc += 2

    def wait(self) -> None:
        """Wait for a key press, store the value of the key in Vx."""
        if not any(self.keypad.pressed_keys):
            self.pc -= 2
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
        """Store BCD representation of Vx in memory locations I, I+1, and I+2."""
        bcd_value = f"{self.v[self.x]:03d}"
        for n in range(3):
            self.ram[self.i + n] = int(bcd_value[n])
