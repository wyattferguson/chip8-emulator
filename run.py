from ctypes import c_uint8 as ubyte

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

        self.VX =  bytearray([0] * 16) # general purpose registers
        self.ram = bytearray([0] * 4096)
        self.stack = [0] * 16

        self.delay_timer = 0
        self.sound_timer = 0

        self.op_code = 0
        self.op_name = ""

        self.addr = 0
        self.x = 0
        self.y = 0
        self.n = 0
        self.kk = 0
        self.lookup = 0

        self.code_lookup = {
            0x1000: self.JMP,
            0x6000: self.LOAD_VX,
        }

        self.rom_file = "test_rom.ch8"


    def load_rom(self):
        print(f"Loading Rom - {self.rom_file}")

        rom_ptr = open(self.rom_file, 'rb')
        rom = rom_ptr.read()

        self.PC = 0x200 # program start in memory
        # print(rom)
        self.ram[self.PC:len(rom)] = bytearray(rom)
        # print(self.ram)
        rom_ptr.close()

    def run(self):
        self.load_rom()

        for i in range(10):
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
            exit()


        self.PC += 2




    def JMP(self):
        self.PC = self.addr
        self.PC -= 2

    def LOAD_VX(self):
        self.VX[self.x] = self.kk


    def vdebug(self, val):
        print(f"{val} {bin(val)} {hex(val)}")


    def debug(self):
        print(f"{self.PC} - {hex(self.lookup)} - {self.op_code} {bin(self.op_code)} {hex(self.op_code)}")


if __name__ == "__main__":
    chip = Chip()
    chip.run()