#import pygame as pg

DISPLAY_SCALER = 4
FPS = 60

SCREEN_WIDTH, SCREEN_HEIGHT = 64, 32


class Chip(object):
    def __init__(self):
        self.PC = 0 # program counter
        self.I = 0  # locations register
        self.VF = 0 # flag register
        self.SP = 0 # stack pointer

        self.V =  bytearray([0] * 16) # general purpose registers
        self.ram = bytearray([0] * 4096) # cpu memory
        self.stack = [0] * 16

        self.delay_timer = 0
        self.sound_timer = 0

        self.op_code = 0 # current instruction

        self.addr = 0
        self.x = 0
        self.y = 0
        self.n = 0
        self.kk = 0
        self.lookup = 0

        self.code_lookup = {
            0x0000: self.JMP_SUB,
            0x00E0: self.CLS, # TODO
            0x00EE: self.RET,
            0x1000: self.JMP,
            0x2000: self.SUB,
            0x3000: self.SE_VX,
            0x4000: self.SNE_VX,
            0x5000: self.SE_VX_VY,
            0x6000: self.LOAD_VX,
            0x7000: self.ADD_VX,
            0x9000: self.SNE_VX_VY,
            0xa000: self.LOAD_I,
            0xd000: self.DRAW, #TODO

        }

        self.rom_file = "test_rom.ch8"


    def load_rom(self):
        print(f"Loading Rom - {self.rom_file}")

        rom_ptr = open(self.rom_file, 'rb')
        rom = rom_ptr.read()

        self.PC = 0x200 # program start in memory
        self.ram[self.PC:len(rom)] = bytearray(rom) # copy rom to ram
        rom_ptr.close()

    def run(self):
        self.load_rom()

        while True:
            self.cycle()


    def decode(self):
        # All instructions are 2 bytes long and are stored most-significant-byte first
        self.op_code = (self.ram[self.PC] << 8) | self.ram[self.PC + 1]

        self.addr = self.op_code & 0x0FFF # lowest 12-bits
        self.n = self.op_code & 0x000F # lowest 4-bits
        self.x = ((self.op_code & 0x0F00) >> 8) & 0xF # lower 4 bits of the high byte
        self.y = ((self.op_code & 0x00F0) >> 4) & 0xF # upper 4 bits of the low byte
        self.kk = self.op_code & 0x00FF # lowest 8 bits
        self.lookup = self.op_code & 0xF000


    def cycle(self):
        self.decode()
        self.debug()
        #self.vdebug(self.lookup)
        try:
            self.code_lookup[self.lookup]()
        except Exception as e:
            # stop on op code error
            print(e)
            exit()

        self.PC += 2 # move program counter to next instruction



    def JMP_SUB(self):
        '''OBSOLETE: Jump to a machine code routine at addr.'''
        self.PC = self.addr


    def CLS(self):
        '''Clear the display.'''
        pass

    def RET(self):
        '''Return from a subroutine.'''
        self.SP -= 1
        self.PC = self.stack[self.SP]

    def JMP(self):
        ''' Move program counter to Addr'''
        self.PC = self.addr
        self.PC -= 2

    def LOAD_VX(self):
        ''' Set register X equal to kk'''
        self.V[self.x] = self.kk

    def LOAD_I(self):
        self.I = self.addr

    def DRAW(self):
        ''' Display n-byte sprite starting at memory location I at (Vx, Vy), set VF = collision.
        '''
        pass

    def SE_VX(self):
        ''' Skip next instruction if Vx = kk. '''
        if self.V[self.x] == self.kk:
            self.PC += 2

    def SNE_VX(self):
        ''' Skip next instruction if Vx != kk. '''
        if self.V[self.x] != self.kk:
            self.PC += 2

    def SE_VX_VY(self):
        '''Skip next instruction if Vx = Vy.'''
        if self.V[self.x] == self.V[self.y]:
            self.PC += 2

    def SNE_VX_VY(self):
        '''Skip next instruction if Vx != Vy.'''
        if self.V[self.x] != self.V[self.y]:
            self.PC += 2

    def SUB(self):
        '''Call subroutine at addr.'''
        self.stack[self.SP] = self.PC
        self.SP += 1
        self.PC = self.addr
        self.PC -= 2 # fix for cycle incrementing PC after

    def ADD_VX(self):
        '''Set Vx = Vx + kk'''
        self.V[self.x] = (self.V[self.x] + self.kk) & 0xFF # get bytes


    def vdebug(self, val):
        print(f"{val} {bin(val)} {hex(val)}")


    def debug(self):
        print(f"{self.PC} - {hex(self.lookup)} - {self.op_code} {bin(self.op_code)} {hex(self.op_code)}")


if __name__ == "__main__":
    chip = Chip()
    chip.run()