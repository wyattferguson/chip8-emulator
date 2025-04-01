import random

from keyboard import Keyboard
from opcodes import OpCode, opcodes
from screen import Screen


class CPU:
    """Chip8 CPU"""

    ram: bytearray = bytearray([0] * 4096)  # 4kb of memory
    v: bytearray = bytearray([0] * 16)  # 16 8-Bit Registers - V0 to VF

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

    def __init__(self, rom: str, screen: Screen, keyboard: Keyboard) -> None:
        self.keyboard: Keyboard = keyboard
        self.screen: Screen = screen
        self.load_font()
        self.load_rom(rom)
        self.opcode = 0

    def load_rom(self, rom: str) -> None:
        """copy ROM into memory"""
        try:
            with open(rom, "rb") as rom_ptr:
                rom_data = rom_ptr.read()
                self.ram[self.pc : self.pc + len(rom_data)] = bytearray(rom_data)
        except Exception as e:
            print("Error loading ROM: ", e)
            exit()

    # fmt: off
    def load_font(self) -> None:
        """copy Chip8 sprite font into memory"""
        font = [
            0xF0, 0x90, 0x90, 0x90, 0xF0,   # 0
            0x20, 0x60, 0x20, 0x20, 0x70,   # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0,   # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0,   # 3
            0x90, 0x90, 0xF0, 0x10, 0x10,   # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0,   # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0,   # 6
            0xF0, 0x10, 0x20, 0x40, 0x40,   # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0,   # 8
            0xF0, 0x90, 0xF0, 0x10, 0xF0,   # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90,   # A
            0xE0, 0x90, 0xE0, 0x90, 0xE0,   # B
            0xF0, 0x80, 0x80, 0x80, 0xF0,   # C
            0xE0, 0x90, 0x90, 0x90, 0xE0,   # D
            0xF0, 0x80, 0xF0, 0x80, 0xF0,   # E
            0xF0, 0x80, 0xF0, 0x80, 0x80    # F
        ]
        self.ram[0 : len(font)] = font
    # fmt: on

    def decode(self) -> None:
        """Retreive and decode next opcode"""

        # Every opcode is 2 bytes long, shift the first 8 bits left
        # Combine it with the next 8 bits to make a full opcode
        self.opcode = (self.ram[self.pc] << 8) | self.ram[self.pc + 1]
        self.x = (self.opcode & 0x0F00) >> 8  # lower 4 bits of the high byte
        self.y = (self.opcode & 0x00F0) >> 4  # upper 4 bits of the low byte
        self.n = self.opcode & 0x000F  # lowest 4 bits of the low byte
        self.addr = self.opcode & 0x0FFF  # lowest 12 bits
        self.kk = self.opcode & 0x00FF  # lowest 8 bits
        self.op_group = self.opcode & 0xF000

    def execute(self) -> None:
        """Execute current opcode"""
        try:
            if self.op_group in [0xE000, 0xF000, 0x0]:
                self.op_group = self.opcode & 0xF0FF
            elif self.op_group == 0x8000:
                self.op_group = self.opcode & 0xF00F

            # last_inst = self.cur_inst
            self.cur_inst = opcodes[self.op_group]
            # if last_inst != self.cur_inst:
            #     print(self.cur_inst, self.v[1], self.v[2])
            if self.cur_inst.args:
                getattr(self, self.cur_inst.call)(*self.cur_inst.args)
            else:
                getattr(self, self.cur_inst.call)()
        except Exception:
            pass

    def cycle(self) -> None:
        """Next CPU instruction"""
        if self.delay_timer > 0:
            self.delay_timer -= 1

        if self.sound_timer > 0:
            self.sound_timer -= 1

        for _ in range(10):
            self.decode()
            self.execute()
            self.pc += 2  # move program counter up 2 bytes to next instruction

    def CLS(self) -> None:
        """Clear screen"""
        self.screen.clear()

    def RET(self) -> None:
        self.pc = self.stack.pop()

    def JMP(self) -> None:
        self.pc = self.addr - 2

    def SUB(self) -> None:
        self.stack.append(self.pc)
        self.pc = self.addr - 2

    def SE_VX(self) -> None:
        if self.v[self.x] == self.kk:
            self.pc += 2

    def SNE_VX(self) -> None:
        if self.v[self.x] != self.kk:
            self.pc += 2

    def SE_VX_VY(self) -> None:
        if self.v[self.x] == self.v[self.y]:
            self.pc += 2

    def LOAD_VX(self) -> None:
        self.v[self.x] = self.kk

    def ADD_VX_KK(self) -> None:
        self.v[self.x] = (self.v[self.x] + self.kk) % 256

    def SET_VX_VY(self) -> None:
        self.v[self.x] = self.v[self.y]

    def OR_VX_VY(self) -> None:
        self.v[self.x] |= self.v[self.y]

    def AND_VX_VY(self) -> None:
        self.v[self.x] &= self.v[self.y]

    def XOR_VX_VY(self) -> None:
        self.v[self.x] ^= self.v[self.y]

    def ADD_VX_VY(self) -> None:
        """Vx = Vx + Vy with carry"""
        sum = self.v[self.x] + self.v[self.y]
        self.v[0xF] = 1 if sum > 255 else 0  # set carry flag
        self.v[self.x] = sum % 256

    def SUB_VX_VY(self) -> None:
        """Vx = Vx - Vy with underflow"""
        sum = self.v[self.x] - self.v[self.y]
        self.v[0xF] = 1 if sum > 0 else 0  # set underflow flag
        self.v[self.x] = sum % 256

    def SUBN_VX_VY(self) -> None:
        """Vx = Vx - Vy with underflow"""
        sum = self.v[self.y] - self.v[self.x]
        self.v[0xF] = 1 if sum > 0 else 0  # set underflow flag
        self.v[self.x] = sum % 256

    def SHR_VX(self) -> None:
        self.v[0xF] = self.v[self.x] & 0x1
        self.v[self.x] >>= 1

    def SHL_VX(self) -> None:
        self.v[0xF] = self.v[self.x] & 0x1
        self.v[self.x] <<= 1

    def SNE_VX_VY(self) -> None:
        if self.v[self.x] != self.v[self.y]:
            self.pc += 2

    def LOAD_I(self) -> None:
        self.i = self.addr

    def JMP_V0_ADDR(self) -> None:
        self.pc = self.addr + self.v[0]

    def RND(self) -> None:
        self.v[self.x] = random.randint(0, 255) & self.kk

    def DRAW(self) -> None:
        self.v[0xF] = 0
        for i in range(self.n):
            sprite = self.ram[self.i + i]
            for j in range(8):
                if sprite & 0x80 and self.screen.set_pixel(self.v[self.x] + j, self.v[self.y] + i):
                    self.v[0xF] = 1

                sprite <<= 1

    def SKP_VX(self, equal: bool) -> None:
        if self.keyboard.pressed_keys[self.v[self.x] & 0xF] == equal:
            self.pc += 2

    def WAIT(self) -> None:
        if not any(self.keyboard.pressed_keys):
            self.pc -= 2
            return

        self.v[self.x] = self.keyboard.pressed_keys.index(True)

    def LOAD_DT_VX(self) -> None:
        self.delay_timer = self.v[self.x]

    def LOAD_ST_VX(self) -> None:
        self.sound_timer = self.v[self.x]

    def LOAD_VX_DT(self) -> None:
        self.v[self.x] = self.delay_timer

    def ADD_I_VX(self) -> None:
        self.i += self.v[self.x]

    def LOAD_VX_I(self) -> None:
        for i in range(self.x + 1):
            self.v[i] = self.ram[self.i + i]

    def LOAD_F_VX(self) -> None:
        self.i = self.v[self.x] * 5

    def LOAD_I_VX(self) -> None:
        """Store registers V0 through Vx in memory starting at location I."""
        for i in range(self.x + 1):
            self.ram[self.i + i] = self.v[i]

    def LOAD_BCD(self) -> None:
        """Store BCD representation of Vx in memory locations I, I+1, and I+2."""
        bcd_value = f"{self.v[self.x]:03d}"
        for n in range(3):
            self.ram[self.i + n] = int(bcd_value[n])
