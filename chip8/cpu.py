import random
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class OpCode:
    label: str  # mnemonic name
    call: str  # CPU method name to call
    args: list = None  # give arguments to send to CPU method

    def __str__(self) -> str:
        return f"{self.label} - {self.call} - {self.args}"


# All standard Chip8 CPU Opcodes
opcodes = {
    0x00E0: OpCode("CLS", "CLS"),
    0x00EE: OpCode("RET", "RET"),
    0x1000: OpCode("JMP addr", "JMP"),
    0x2000: OpCode("CALL addr", "SUB"),
    0x3000: OpCode("SE Vx, kk", "SE_VX"),
    0x4000: OpCode("SNE Vx, kk", "SNE_VX"),
    0x5000: OpCode("SE Vx, Vy", "SE_VX_VY"),
    0x6000: OpCode("LD Vx, kk", "LOAD_VX"),
    0x7000: OpCode("ADD Vx, kk", "ADD_VX_KK"),
    0x8000: OpCode("LD Vx, Vy", "SET_VX_VY"),
    0x8001: OpCode("OR Vx, Vy", "OR_VX_VY"),
    0x8002: OpCode("AND Vx, Vy", "AND_VX_VY"),
    0x8003: OpCode("XOR Vx, Vy", "XOR_VX_VY"),
    0x8004: OpCode("ADD Vx, Vy", "ADD_VX_VY"),
    0x8005: OpCode("SUB Vx, Vy", "SUB_VX_VY"),
    0x8006: OpCode("SHR Vx {, Vy}", "SHR_VX"),
    0x8007: OpCode("SUBN Vx, Vy", "SUBN_VX_VY"),
    0x800E: OpCode("SHL Vx {, Vy}", "SHL_VX"),
    0x9000: OpCode("SNE Vx, Vy", "SNE_VX_VY"),
    0xA000: OpCode("LD I, addr", "LOAD_I"),
    0xB000: OpCode("JP V0, addr", "JMP_V0_ADDR"),
    0xC000: OpCode("RND Vx, kk", "RND"),
    0xD000: OpCode("DRW Vx, Vy, n", "DRAW"),
    0xE09E: OpCode("SKP VX", "SKP_VX", [True]),
    0xE0A1: OpCode("SKNP Vx", "SKP_VX", [False]),
    0xF007: OpCode("LD Vx, DT", "LOAD_VX_DT"),
    0xF00A: OpCode("WAIT", "WAIT"),
    0xF015: OpCode("LD DT, Vx", "LOAD_DT_VX"),
    0xF018: OpCode("LD ST, Vx", "LOAD_ST_VX"),
    0xF01E: OpCode("ADD I, Vx", "ADD_I_VX"),
    0xF029: OpCode("LD F, Vx", "LOAD_F_VX"),
    0xF033: OpCode("LD B, Vx", "LOAD_BCD"),
    0xF055: OpCode("LD [I], Vx", "LOAD_I_VX"),
    0xF065: OpCode("LD Vx, [I]", "LOAD_VX_I"),
}


class CPU(object):
    """Chip8 CPU"""

    ram = bytearray([0] * 4096)  # 4kb of memory
    v = bytearray([0] * 16)  # 16 8-Bit Registers - V0 to VF

    i = 0  # 12bit register
    x = 0  # 4-bit register
    y = 0  # 4-bit register
    n = 0  # lowest 4 bits of the instruction
    addr = 0  # lowest 12 bits of the instruction
    kk = 0  # lowest 8 bits of the instruction
    op_group = 0  # opcode group the instruction belongs to

    cur_inst = False  # current instruction being run
    stack = []  # Store return addresses when subroutines are called
    sound_timer = 0  # Play a beep when > 0
    delay_timer = 0

    pc = 0x200  # program counter, starts at 0x200 in ram

    def __init__(self, rom, screen, keyboard):
        self.keyboard = keyboard
        self.screen = screen
        self.load_font()
        self.load_rom(rom)
        self.opcode = 0

    def load_rom(self, rom):
        """copy ROM into memory"""
        rom_ptr = open(rom, "rb")
        rom = rom_ptr.read()
        self.ram[self.pc : len(rom)] = bytearray(rom)
        rom_ptr.close()

    # fmt: off
    def load_font(self):
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

    def decode(self):
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

    def execute(self):
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
        except Exception as e:
            pass

    def cycle(self):
        """Next CPU instruction"""
        if self.delay_timer > 0:
            self.delay_timer -= 1

        if self.sound_timer > 0:
            self.sound_timer -= 1

        for i in range(10):
            self.decode()
            self.execute()
            self.pc += 2  # move program counter up 2 bytes to next instruction

    def CLS(self):
        """Clear screen"""
        self.screen.clear()

    def RET(self):
        self.pc = self.stack.pop()

    def JMP(self):
        self.pc = self.addr - 2

    def SUB(self):
        self.stack.append(self.pc)
        self.pc = self.addr - 2

    def SE_VX(self):
        if self.v[self.x] == self.kk:
            self.pc += 2

    def SNE_VX(self):
        if self.v[self.x] != self.kk:
            self.pc += 2

    def SE_VX_VY(self):
        if self.v[self.x] == self.v[self.y]:
            self.pc += 2

    def LOAD_VX(self):
        self.v[self.x] = self.kk

    def ADD_VX_KK(self):
        self.v[self.x] = (self.v[self.x] + self.kk) % 256

    def SET_VX_VY(self):
        self.v[self.x] = self.v[self.y]

    def OR_VX_VY(self):
        self.v[self.x] |= self.v[self.y]

    def AND_VX_VY(self):
        self.v[self.x] &= self.v[self.y]

    def XOR_VX_VY(self):
        self.v[self.x] ^= self.v[self.y]

    def ADD_VX_VY(self):
        """Vx = Vx + Vy with carry"""
        sum = self.v[self.x] + self.v[self.y]
        self.v[0xF] = 1 if sum > 255 else 0  # set carry flag
        self.v[self.x] = sum % 256

    def SUB_VX_VY(self):
        """Vx = Vx - Vy with underflow"""
        sum = self.v[self.x] - self.v[self.y]
        self.v[0xF] = 1 if sum > 0 else 0  # set underflow flag
        self.v[self.x] = sum % 256

    def SUBN_VX_VY(self):
        """Vx = Vx - Vy with underflow"""
        sum = self.v[self.y] - self.v[self.x]
        self.v[0xF] = 1 if sum > 0 else 0  # set underflow flag
        self.v[self.x] = sum % 256

    def SHR_VX(self):
        self.v[0xF] = self.v[self.x] & 0x1
        self.v[self.x] >>= 1

    def SHL_VX(self):
        self.v[0xF] = self.v[self.x] & 0x1
        self.v[self.x] <<= 1

    def SNE_VX_VY(self):
        if self.v[self.x] != self.v[self.y]:
            self.pc += 2

    def LOAD_I(self):
        self.i = self.addr

    def JMP_V0_ADDR(self):
        self.pc = self.addr + self.v[0]

    def RND(self):
        self.v[self.x] = random.randint(0, 255) & self.kk

    def DRAW(self):
        self.v[0xF] = 0
        for i in range(self.n):
            sprite = self.ram[self.i + i]
            for j in range(8):
                if sprite & 0x80:
                    if self.screen.set_pixel(self.v[self.x] + j, self.v[self.y] + i):
                        self.v[0xF] = 1

                sprite <<= 1

    def SKP_VX(self, equal: bool):
        if self.keyboard.pressed_keys[self.v[self.x] & 0xF] == equal:
            self.pc += 2

    def WAIT(self):
        if not any(self.keyboard.pressed_keys):
            self.pc -= 2
            return

        self.v[self.x] = self.keyboard.pressed_keys.index(True)

    def LOAD_DT_VX(self):
        self.delay_timer = self.v[self.x]

    def LOAD_ST_VX(self):
        self.sound_timer = self.v[self.x]

    def LOAD_VX_DT(self):
        self.v[self.x] = self.delay_timer

    def ADD_I_VX(self):
        self.i += self.v[self.x]

    def LOAD_VX_I(self):
        for i in range(self.x + 1):
            self.v[i] = self.ram[self.i + i]

    def LOAD_F_VX(self):
        self.i = self.v[self.x] * 5

    def LOAD_I_VX(self):
        """Store registers V0 through Vx in memory starting at location I."""
        for i in range(self.x + 1):
            self.ram[self.i + i] = self.v[i]

    def LOAD_BCD(self):
        """Store BCD representation of Vx in memory locations I, I+1, and I+2."""
        bcd_value = "{:03d}".format(self.v[self.x])
        for n in range(3):
            self.ram[self.i + n] = int(bcd_value[n])
