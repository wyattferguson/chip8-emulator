from random import randbytes, randint

import pygame as pg

from config import *


class Chip(object):
    def __init__(self):
        self.PC = 0 # program counter
        self.I = 0  # locations register
        self.VF = REGISTERS - 1 # flag register
        self.SP = 0 # stack pointer

        self.V = bytearray([0] * REGISTERS) # 16 general purpose registers
        self.ram = bytearray([0] * MEMORY) # 4kb of memory
        self.stack = [0] * REGISTERS

        self.delay_timer = 0
        self.sound_timer = 0

        self.op_code = 0 # current instruction
        self.addr = 0
        self.x = 0
        self.y = 0
        self.n = 0
        self.kk = 0
        self.lookup = 0

        # primary instuction set
        self.code_lookup = {
            0x0000: self.EXTRAS,
            0x1000: self.JMP,
            0x2000: self.SUB,
            0x3000: self.SE_VX,
            0x4000: self.SNE_VX,
            0x5000: self.SE_VX_VY,
            0x6000: self.LOAD_VX,
            0x7000: self.ADD_VX_KK,
            0x8000: self.LOGICAL,
            0x9000: self.SNE_VX_VY,
            0xa000: self.LOAD_I,
            0xc000: self.RND,
            0xd000: self.DRAW, #TODO
            0xf000: self.EXTRAS,
        }

        # 0x8XXX specific operations
        self.logical_lookup = {
            0x0: self.SET_VX_VY, # 8xy0
            0x1: self.OR_VX_VY,
            0x2: self.AND_VX_VY,
            0x3: self.XOR_VX_VY,
            0x4: self.ADD_VX_VY,
            0x5: self.SUB_VX_VY,
            0x6: self.SHR_VX,
            0x7: self.SUBN_VX_VY,
            0xe: self.SHL_VX
        }

        # misc sub instructions
        self.extra_lookup = {
            0x0007: self.SET_VX_DT,
            0x0015: self.LOAD_DT,
            0x0018: self.LOAD_ST,
            0x0029: self.LOAD_F_VX,
            0x0030: self.LOAD_I_VX_EXT,
            0x0033: self.LOAD_BCD,
            0x0055: self.LOAD_I_VX,
            0x0065: self.LOAD_VX_I,
            0x00e0: self.CLS,
            0x00ee: self.RET,
            0x001e: self.ADD_I_VX
        }

        self.rom_file = "./roms/tetris.ch8"

        pg.init()
        pg.display.set_caption(f"Chip8 - {self.rom_file}")

        self.screen_size = ( SCREEN_WIDTH * DISPLAY_SCALER, SCREEN_HEIGHT * DISPLAY_SCALER)
        self.screen = pg.display.set_mode(self.screen_size)
        self.clock = pg.time.Clock()
        self.tick_speed = FPS
        self.running = True


    def load_rom(self):
        print(f"Loading Rom - {self.rom_file}")

        rom_ptr = open(self.rom_file, 'rb')
        rom = rom_ptr.read()

        self.PC = PROGRAM_START # program start in memory
        self.ram[self.PC:len(rom)] = bytearray(rom) # copy rom to ram
        rom_ptr.close()


    def screen_update(self):
        # self.should_quit()
        pg.display.update()
        self.clock.tick(self.tick_speed)

    def run(self):
        self.load_rom()

        while self.running:
            self.cycle()
            self.screen_update()

        pg.quit()



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
        pass


    def CLS(self):
        '''Clear the display.'''
        self.screen.fill(BLACK)

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

        for y_index in range(self.n):
            y_coord = self.y + y_index
            y_coord = y_coord % SCREEN_HEIGHT

            for x_index in range(8):
                x_coord = self.x + x_index
                x_coord = x_coord % SCREEN_WIDTH

                x_base = x_coord * DISPLAY_SCALER
                y_base = y_coord * DISPLAY_SCALER
                pg.draw.rect(self.screen, WHITE, (x_base,y_base, DISPLAY_SCALER, DISPLAY_SCALER))



    def RND(self):
        '''Set Vx = random byte AND kk.'''
        self.V[self.x] = randint(0, 255) & self.kk


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

    def ADD_VX_KK(self):
        '''Set Vx = Vx + kk'''
        self.V[self.x] = (self.V[self.x] + self.kk) & 0xFF # get bytes

    def EXTRAS(self):
        print("EXTRA ", self.kk, hex(self.lookup))
        self.extra_lookup[self.kk]()

    def LOGICAL(self):
        print("LOGICAL ", self.n, hex(self.n))
        self.logical_lookup[self.n]()

    def OR_VX_VY(self):
        '''Set Vx = Vx OR Vy.'''
        self.V[self.x] = self.V[self.x] | self.V[self.y]

    def AND_VX_VY(self):
        '''Set Vx = Vx AND Vy.'''
        self.V[self.x] = self.V[self.x] & self.V[self.y]

    def XOR_VX_VY(self):
        '''Set Vx = Vx XOR Vy.'''
        self.V[self.x]  = self.V[self.x] ^ self.V[self.y]

    def ADD_VX_VY(self):
        '''Set Vx = Vx + Vy, set VF = carry.'''
        value = self.V[self.x] + self.V[self.y]
        self.V[self.VF] = 1 if value > 255 else 0 # set carry flag
        self.V[self.x] = value & 0xFF

    def SUB_VX_VY(self):
        '''Set Vx = Vx - Vy, set VF = NOT borrow.'''
        value = self.V[self.x] - self.V[self.y]
        self.V[self.VF] = 1 if self.V[self.x] > self.V[self.y] else 0 # set carry flag
        self.V[self.x]  = value & 0xFF

    def SUBN_VX_VY(self):
        '''Set Vx = Vy - Vx, set VF = NOT borrow.'''
        value = self.V[self.y] - self.V[self.x]
        self.V[self.VF] = 1 if self.V[self.y] > self.V[self.x] else 0 # set carry flag
        self.V[self.x]  = value & 0xFF

    def SHR_VX(self):
        '''Set Vx = Vx SHR 1.'''
        self.V[self.x] = self.V[self.x] >> 1

    def SHL_VX(self):
        '''Set Vx = Vx SHL 1.'''
        self.V[self.x] = (self.V[self.x] << 1) & 0xFF

    def LOAD_ST(self):
        '''Set sound timer = Vx.'''
        self.sound_timer = self.V[self.x]

    def LOAD_DT(self):
        '''Set delay timer = Vx.'''
        self.delay_timer = self.V[self.x]

    def LOAD_I_VX_EXT(self):
        ''' Load I with the sprite indicated in the X register. All sprites are 10 bytes long'''
        self.I = self.V[self.x] * 10

    def SET_VX_VY(self):
        '''Set Vx = Vy.'''
        self.V[self.x] = self.V[self.y]

    def ADD_I_VX(self):
        '''Set I = I + Vx.'''
        self.I = self.I + self.V[self.x]

    def SET_VX_DT(self):
        '''Set Vx = delay timer value.'''
        self.V[self.x] = self.delay_timer

    def LOAD_VX_I(self):
        '''Read registers V0 through Vx from memory starting at location I.'''
        for i in range(0,self.x+1):
            self.V[i] = self.ram[self.I + i]
            # print(i, self.V[i], self.I + i, self.ram[self.I + i])

    def LOAD_F_VX(self):
        '''Set I = location of sprite for digit Vx. All sprites are 5 bytes long'''
        self.I = self.V[self.x] * 5

    def LOAD_I_VX(self):
        '''Store registers V0 through Vx in memory starting at location I.'''
        for i in range(0,self.x+1):
            self.ram[self.I + i] = self.V[i]

    def LOAD_BCD(self):
        '''Store BCD representation of Vx in memory locations I, I+1, and I+2.'''

        bcd_value = '{:03d}'.format(self.V[self.x])
        self.ram[self.I] = int(bcd_value[0])
        self.ram[self.I + 1] = int(bcd_value[1])
        self.ram[self.I + 2] = int(bcd_value[2])


    def vdebug(self, val):
        print(f"{val} {bin(val)} {hex(val)}")


    def debug(self):
        print(f"{self.PC} - {hex(self.lookup)} - {self.op_code} {bin(self.op_code)} {hex(self.op_code)}")


if __name__ == "__main__":
    chip = Chip()
    chip.run()