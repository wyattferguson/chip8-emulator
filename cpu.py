from random import randint

from config import DEBUG, FONT, MEMORY, PROGRAM_START, REGISTERS
from opcodes import OPCODES


class ChipCPU(object):
    def __init__(self, screen):
        self.PC = 0x0  # program counter
        self.I = 0x0  # locations register
        self.VF = REGISTERS - 1  # flag register
        self.SP = 0x0  # stack pointer

        self.V = bytearray([0] * REGISTERS)  # 16 general purpose registers
        self.ram = bytearray([0] * MEMORY)  # 4kb of memory
        self.stack = [0] * REGISTERS

        self.delay_timer = 0

        self.op_code = 0  # current instruction
        self.addr = 0
        self.x = 0
        self.y = 0
        self.n = 0
        self.kk = 0
        self.lookup = 0
        self.cur_inst = False
        self.ram[:len(FONT)] = bytearray(FONT)

        self.screen = screen

    def load_rom(self, rom_file: str):
        '''Load .ch8 ROM into memory'''
        rom_ptr = open(rom_file, 'rb')
        rom = rom_ptr.read()

        self.PC = PROGRAM_START  # program start in memory
        self.ram[self.PC:len(rom)] = bytearray(rom)  # copy rom to ram
        rom_ptr.close()

    def decode(self):
        # All instructions are 2 bytes long and are stored most-significant-byte first
        self.op_code = (self.ram[self.PC] << 8) | self.ram[self.PC + 1]

        self.addr = self.op_code & 0x0FFF  # lowest 12-bits
        self.n = self.op_code & 0x000F  # lowest 4-bits
        # lower 4 bits of the high byte
        self.x = ((self.op_code & 0x0F00) >> 8) & 0xF
        # upper 4 bits of the low byte
        self.y = ((self.op_code & 0x00F0) >> 4) & 0xF
        self.kk = self.op_code & 0x00FF  # lowest 8 bits
        self.lookup = self.op_code & 0xF000

    def execute(self):
        try:
            args = []
            lookup_code = self.lookup
            if self.lookup in [0xe000, 0xf000, 0x0]:
                lookup_code = self.op_code & 0xF0FF
            elif self.lookup == 0x8000:
                lookup_code = self.op_code & 0xF00F

            self.cur_inst = OPCODES[lookup_code]
            args = self.cur_inst.args
            if args:
                getattr(self, self.cur_inst.call)(*args)
            else:
                getattr(self, self.cur_inst.call)()
        except Exception as e:
            # stop on op code error
            print(e)
            exit()

    def cycle(self):
        '''Execute next CPU cycle'''
        if self.delay_timer:
            self.delay_timer -= 1

        self.decode()
        self.execute()

        if DEBUG:
            print(self)

        self.PC += 2  # move program counter to next instruction

    def CLS(self):
        '''Clear the display.'''
        self.screen.clear_screen()

    def RET(self):
        '''Return from a subroutine.'''
        self.SP -= 1
        self.PC = self.stack[self.SP]

    def JMP(self):
        ''' Move program counter to Addr'''
        self.PC = self.addr - 2

    def SUB(self):
        '''Call subroutine at addr.'''
        self.stack[self.SP] = self.PC
        self.SP += 1
        self.JMP()

    def SE_VX(self, equal: bool):
        ''' Skip next instruction if Vx !/= kk. '''
        self.PC += 2 if (self.V[self.x] == self.kk) == equal else 0

    def SE_VX_VY(self, equal: bool):
        '''Skip next instruction if Vx !/= Vy.'''
        self.PC += 2 if (self.V[self.x] == self.V[self.y]) == equal else 0

    def LOAD_VX(self):
        ''' Set register X equal to kk'''
        self.V[self.x] = self.kk

    def ADD_VX_KK(self):
        '''Set Vx = Vx + kk'''
        self.V[self.x] = (self.V[self.x] + self.kk) & 0xFF

    def SET_VX_VY(self):
        '''Set Vx = Vy.'''
        self.V[self.x] = self.V[self.y]

    def OR_VX_VY(self):
        '''Set Vx = Vx OR Vy.'''
        self.V[self.x] = self.V[self.x] | self.V[self.y]

    def AND_VX_VY(self):
        '''Set Vx = Vx AND Vy.'''
        self.V[self.x] = self.V[self.x] & self.V[self.y]

    def XOR_VX_VY(self):
        '''Set Vx = Vx XOR Vy.'''
        self.V[self.x] = self.V[self.x] ^ self.V[self.y]

    def ADD_VX_VY(self):
        '''Set Vx = Vx + Vy, set VF = carry.'''
        value = self.V[self.x] + self.V[self.y]
        self.V[self.VF] = 1 if value > 255 else 0  # set carry flag
        self.V[self.x] = value & 0xFF

    def SHR_VX(self):
        '''Set Vx = Vx SHR 1.'''
        self.V[self.x] = self.V[self.x] >> 1

    def SUB_VX_VY(self, reg_a: str, reg_b: str):
        '''Set Vx = Vx - Vy, set VF = NOT borrow.'''
        source = getattr(self, reg_a)
        target = getattr(self, reg_b)
        value = self.V[source] - self.V[target]
        # set carry flag
        self.V[self.VF] = 1 if self.V[source] > self.V[target] else 0
        self.V[source] = value & 0xFF

    def SHL_VX(self):
        '''Set Vx = Vx SHL 1.'''
        self.V[self.x] = (self.V[self.x] << 1) & 0xFF

    def LOAD_I(self):
        '''Set I = addr.'''
        self.I = self.addr

    def JMP_V0_ADDR(self):
        '''Jump to location addr + V0.'''
        self.PC = self.addr + self.V[0] - 2

    def RND(self):
        '''Set Vx = random byte AND kk.'''
        self.V[self.x] = (randint(0, 255) & self.kk) & 0xFF

    def DRAW(self):
        ''' Display n-byte sprite starting at memory location I at (Vx, Vy),
        set VF = collision.
        '''
        self.V[self.VF] = 0

        y_pos = self.V[self.y] % 32

        for row in range(self.n):
            x_pos = self.V[self.x] % 64

            sprite_byte = self.ram[self.I + row]
            sprite_bits = bin(sprite_byte)[2:].zfill(8)

            for bit in sprite_bits:
                if bit == '1':
                    self.V[self.VF] = self.screen.flip(x_pos, y_pos)

                x_pos += 1
                if x_pos > 63:
                    break

            y_pos += 1
            if y_pos > 31:
                break

    def SKP_VX(self, equal: bool):
        '''Skip next instruction if key with the value of Vx is pressed.'''
        if self.screen.pressed_keys[self.V[self.x] & 0xF] == equal:
            self.PC += 2

    def LOAD_VX_DT(self):
        '''Set Vx = delay timer value.'''
        self.V[self.x] = self.delay_timer

    def WAIT(self):
        '''Wait for a key press, store the value of the key in Vx.'''
        if not any(self.screen.pressed_keys):
            self.PC -= 2
            return False

        self.V[self.x] = self.screen.pressed_keys.index(True)

    def LOAD_DT_VX(self):
        '''Set delay timer = Vx.'''
        self.delay_timer = self.V[self.x]

    def LOAD_ST_VX(self):
        '''Set sound timer = Vx.'''
        pass

    def ADD_I_VX(self):
        '''Set I = I + Vx.'''
        self.I = self.I + self.V[self.x]

    def LOAD_VX_I(self):
        '''Read registers V0 through Vx from memory starting at location I.'''
        for i in range(self.x + 1):
            self.V[i] = self.ram[self.I + i]

    def LOAD_F_VX(self):
        '''Set I = location of sprite for digit Vx. All sprites are 5 bytes long'''
        self.I = self.V[self.x] * 5

    def LOAD_I_VX(self):
        '''Store registers V0 through Vx in memory starting at location I.'''
        for i in range(self.x + 1):
            self.ram[self.I + i] = self.V[i]

    def LOAD_BCD(self):
        '''Store BCD representation of Vx in memory locations I, I+1, and I+2.'''
        bcd_value = '{:03d}'.format(self.V[self.x])
        for n in range(3):
            self.ram[self.I + n] = int(bcd_value[n])

    def __str__(self):
        return (f"{self.PC}-{self.SP}-{hex(self.addr)}-{hex(self.op_code)}-{self.cur_inst.call}")
