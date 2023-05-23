from random import randint

import pygame as pg

from config import *


class Chip(object):
    def __init__(self):
        self.PC = 0  # program counter
        self.I = 0  # locations register
        self.VF = REGISTERS - 1  # flag register
        self.SP = 0  # stack pointer

        self.V = bytearray([0] * REGISTERS)  # 16 general purpose registers
        self.ram = bytearray([0] * MEMORY)  # 4kb of memory
        self.stack = [0] * REGISTERS

        self.delay_timer = 0
        self.sound_timer = 0

        self.op_code = 0  # current instruction
        self.op_name = ""
        self.addr = 0
        self.x = 0
        self.y = 0
        self.n = 0
        self.kk = 0
        self.lookup = 0

        # primary operations set
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
            0xb000: self.JMP_V0_ADDR,
            0xc000: self.RND,
            0xd000: self.DRAW,
            0xe000: self.EXTRAS,
            0xf000: self.EXTRAS,
        }

        # 0x800X specific operations
        self.logical_lookup = {
            0x0: self.SET_VX_VY,  # 8xy0
            0x1: self.OR_VX_VY,
            0x2: self.AND_VX_VY,
            0x3: self.XOR_VX_VY,
            0x4: self.ADD_VX_VY,
            0x5: self.SUB_VX_VY,
            0x6: self.SHR_VX,
            0x7: self.SUBN_VX_VY,
            0xe: self.SHL_VX
        }

        '''
        Super Chip-48 Instructions TODO
        00Cn - SCD nibble
        00FB - SCR
        00FC - SCL
        00FD - EXIT
        00FE - LOW
        00FF - HIGH
        Dxy0 - DRW Vx, Vy, 0
        Fx75 - LD R, Vx
        Fx85 - LD Vx, R
        '''

        # 0x0/0xe/0xf operations
        self.extra_lookup = {
            0x0007: self.LOAD_VX_DT,
            0x000e: self.SKIP,  # TODO
            0x000a: self.WAIT,  # TODO
            0x00a1: self.SKNP,  # TODO
            0x0015: self.LOAD_DT_VX,
            0x0018: self.LOAD_ST_VX,
            0x0029: self.LOAD_F_VX,
            0x0030: self.LOAD_I_VX_EXT,
            0x0033: self.LOAD_BCD,
            0x0055: self.LOAD_I_VX,
            0x0065: self.LOAD_VX_I,
            0x00e0: self.CLS,
            0x00ee: self.RET,
            0x001e: self.ADD_I_VX
        }

        self.rom_file = ROM_FILE

        pg.init()
        pg.display.set_caption(f"Chip8 - {self.rom_file}")

        self.screen_size = (SCREEN_WIDTH * DISPLAY_SCALER, SCREEN_HEIGHT * DISPLAY_SCALER)
        self.screen = pg.display.set_mode(self.screen_size)
        self.clock = pg.time.Clock()
        self.tick_speed = FPS
        self.running = True

    def load_rom(self):
        print(f"Loading Rom - {self.rom_file}")

        rom_ptr = open(self.rom_file, 'rb')
        rom = rom_ptr.read()

        self.PC = PROGRAM_START  # program start in memory
        self.ram[self.PC:len(rom)] = bytearray(rom)  # copy rom to ram
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

        self.addr = self.op_code & 0x0FFF  # lowest 12-bits
        self.n = self.op_code & 0x000F  # lowest 4-bits
        self.x = ((self.op_code & 0x0F00) >> 8) & 0xF  # lower 4 bits of the high byte
        self.y = ((self.op_code & 0x00F0) >> 4) & 0xF  # upper 4 bits of the low byte
        self.kk = self.op_code & 0x00FF  # lowest 8 bits
        self.lookup = self.op_code & 0xF000

    def cycle(self):
        self.decode()
        self.debug()

        try:
            self.code_lookup[self.lookup]()
        except Exception as e:
            # stop on op code error
            print(e)
            exit()

        self.PC += 2  # move program counter to next instruction

    def CLS(self):
        '''Clear the display.'''
        self.screen.fill(BLACK)
        self.op_name = "CLS"

    def RET(self):
        '''Return from a subroutine.'''
        self.SP -= 1
        self.PC = self.stack[self.SP]
        self.op_name = "RET"

    def JMP(self):
        ''' Move program counter to Addr'''
        self.PC = self.addr
        self.PC -= 2
        self.op_name = "JP addr"

    def SUB(self):
        '''Call subroutine at addr.'''
        self.stack[self.SP] = self.PC
        self.SP += 1
        self.PC = self.addr
        self.PC -= 2  # fix for cycle incrementing PC after
        self.op_name = "CALL addr"

    def SE_VX(self):
        ''' Skip next instruction if Vx = kk. '''
        if self.V[self.x] == self.kk:
            self.PC += 2
        self.op_name = "SE Vx, kk"

    def SNE_VX(self):
        ''' Skip next instruction if Vx != kk. '''
        if self.V[self.x] != self.kk:
            self.PC += 2
        self.op_name = "SNE Vx, kk"

    def SE_VX_VY(self):
        '''Skip next instruction if Vx = Vy.'''
        if self.V[self.x] == self.V[self.y]:
            self.PC += 2
        self.op_name = "SE Vx, Vy"

    def LOAD_VX(self):
        ''' Set register X equal to kk'''
        self.V[self.x] = self.kk
        self.op_name = "LD Vx, kk"

    def ADD_VX_KK(self):
        '''Set Vx = Vx + kk'''
        self.V[self.x] = (self.V[self.x] + self.kk) & 0xFF
        self.op_name = "ADD Vx, kk"

    def SET_VX_VY(self):
        '''Set Vx = Vy.'''
        self.V[self.x] = self.V[self.y]
        self.op_name = "LD Vx, Vy"

    def OR_VX_VY(self):
        '''Set Vx = Vx OR Vy.'''
        self.V[self.x] = self.V[self.x] | self.V[self.y]
        self.op_name = "OR Vx, Vy"

    def AND_VX_VY(self):
        '''Set Vx = Vx AND Vy.'''
        self.V[self.x] = self.V[self.x] & self.V[self.y]
        self.op_name = "AND Vx, Vy"

    def XOR_VX_VY(self):
        '''Set Vx = Vx XOR Vy.'''
        self.V[self.x] = self.V[self.x] ^ self.V[self.y]
        self.op_name = "XOR Vx, Vy"

    def ADD_VX_VY(self):
        '''Set Vx = Vx + Vy, set VF = carry.'''
        value = self.V[self.x] + self.V[self.y]
        self.V[self.VF] = 1 if value > 255 else 0  # set carry flag
        self.V[self.x] = value & 0xFF
        self.op_name = "ADD Vx, Vy"

    def SUB_VX_VY(self):
        '''Set Vx = Vx - Vy, set VF = NOT borrow.'''
        value = self.V[self.x] - self.V[self.y]
        self.V[self.VF] = 1 if self.V[self.x] > self.V[self.y] else 0  # set carry flag
        self.V[self.x] = value & 0xFF
        self.op_name = "SUB Vx, Vy"

    def SHR_VX(self):
        '''Set Vx = Vx SHR 1.'''
        self.V[self.x] = self.V[self.x] >> 1
        self.op_name = "SHR Vx {, Vy}"

    def SUBN_VX_VY(self):
        '''Set Vx = Vy - Vx, set VF = NOT borrow.'''
        value = self.V[self.y] - self.V[self.x]
        self.V[self.VF] = 1 if self.V[self.y] > self.V[self.x] else 0  # set carry flag
        self.V[self.x] = value & 0xFF
        self.op_name = "SUBN Vx, Vy"

    def SHL_VX(self):
        '''Set Vx = Vx SHL 1.'''
        self.V[self.x] = (self.V[self.x] << 1) & 0xFF
        self.op_name = "SHL Vx {, Vy}"

    def SNE_VX_VY(self):
        '''Skip next instruction if Vx != Vy.'''
        if self.V[self.x] != self.V[self.y]:
            self.PC += 2
        self.op_name = "SNE Vx, Vy"

    def LOAD_I(self):
        '''Set I = addr.'''
        self.I = self.addr
        self.op_name = "LD I, addr"

    def JMP_V0_ADDR(self):
        '''Jump to location addr + V0.'''
        self.PC = self.addr + self.V[0]
        self.op_name = "JP V0, addr"

    def RND(self):
        '''Set Vx = random byte AND kk.'''
        self.V[self.x] = randint(0, 255) & self.kk
        self.op_name = "RND Vx, kk"

    def DRAW(self):
        ''' Display n-byte sprite starting at memory location I at (Vx, Vy),
        set VF = collision.
        '''

        for y_index in range(self.n):
            y_coord = self.y + y_index
            y_coord = y_coord % SCREEN_HEIGHT

            for x_index in range(8):
                x_coord = self.x + x_index
                x_coord = x_coord % SCREEN_WIDTH

                x_base = x_coord * DISPLAY_SCALER
                y_base = y_coord * DISPLAY_SCALER
                pg.draw.rect(self.screen, WHITE, (x_base, y_base, DISPLAY_SCALER, DISPLAY_SCALER))

        self.op_name = "DRW Vx, Vy, n"

    # TODO
    def SKIP(self):
        '''Skip next instruction if key with the value of Vx is pressed.'''

        self.op_name = "SKP Vx"

    # TODO
    def SKNP(self):
        '''Skip next instruction if key with the value of Vx is not pressed.'''
        self.op_name = "SKNP Vx"

    def LOAD_VX_DT(self):
        '''Set Vx = delay timer value.'''
        self.V[self.x] = self.delay_timer
        self.op_name = "LD Vx, DT"

    # TODO
    def WAIT(self):
        '''Wait for a key press, store the value of the key in Vx.'''
        self.op_name = "LD Vx, K"

    def LOAD_DT_VX(self):
        '''Set delay timer = Vx.'''
        self.delay_timer = self.V[self.x]
        self.op_name = "LD DT, Vx"

    def LOAD_ST_VX(self):
        '''Set sound timer = Vx.'''
        self.sound_timer = self.V[self.x]
        self.op_name = "LD ST, Vx"

    def ADD_I_VX(self):
        '''Set I = I + Vx.'''
        self.I = self.I + self.V[self.x]
        self.op_name = "ADD I, Vx"

    def LOAD_VX_I(self):
        '''Read registers V0 through Vx from memory starting at location I.'''
        for i in range(0, self.x + 1):
            self.V[i] = self.ram[self.I + i]
        self.op_name = "LD Vx, [I]"

    def LOAD_F_VX(self):
        '''Set I = location of sprite for digit Vx. All sprites are 5 bytes long'''
        self.I = self.V[self.x] * 5
        self.op_name = "LD F, Vx"

    def LOAD_I_VX(self):
        '''Store registers V0 through Vx in memory starting at location I.'''
        for i in range(0, self.x + 1):
            self.ram[self.I + i] = self.V[i]
        self.op_name = "LD [I], Vx"

    def LOAD_BCD(self):
        '''Store BCD representation of Vx in memory locations I, I+1, and I+2.'''
        bcd_value = '{:03d}'.format(self.V[self.x])
        self.ram[self.I] = int(bcd_value[0])
        self.ram[self.I + 1] = int(bcd_value[1])
        self.ram[self.I + 2] = int(bcd_value[2])
        self.op_name = "LD B, Vx"

    def LOAD_I_VX_EXT(self):
        '''Load I with the sprite indicated in the X register.
        All sprites are 10 bytes long.
        '''
        self.I = self.V[self.x] * 10
        self.op_name = "LD HF, Vx"

    def EXTRAS(self):
        self.extra_lookup[self.kk]()

    def LOGICAL(self):
        self.logical_lookup[self.n]()

    def vdebug(self, val):
        print(f"{val} {bin(val)} {hex(val)}")

    def debug(self):
        print(f"""{self.PC} - {self.SP} - {hex(self.lookup)} -
              {self.op_code} {hex(self.op_code)} - {self.op_name}""")


if __name__ == "__main__":
    chip = Chip()
    chip.run()
