

import pygame
import os
from random import randint, seed, randrange
from time import time, sleep
from pprint import pprint
import collections


os.environ['SDL_VIDEODRIVER'] = 'directx'

from pygame.constants import K_SPACE, K_RETURN
import colorama             # USED for that F... screen CLEAR

colorama.init()

import winsound
Freq = 3500  # Set Frequency To 2500 Hertz
Dur = 20  # Set Duration To 1000 ms == 1 second

# Find out what byte order your system uses
import sys
print "Native byteorder: ", sys.byteorder

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)s - %(message)s')  # %(asctime)s

logger = logging.getLogger()

logger.setLevel(logging.CRITICAL)
# logger.setLevel(logging.DEBUG)
# logger.setLevel(logging.INFO)
logger.setLevel(logging.WARN)

# Center the app window on the Desktop
os.environ['SDL_VIDEO_CENTERED'] = '1'

# Initialize the game engine
pygame.init()


# CONFIG: see the file "config.txt"
# Set all except PYGAME_DISPLAY to [False] for better performance
# Choose PYGAME_DISPLAY or TEST_VRAM as True - not both at the moment, cause of the single scaling factor

from configparser import ConfigParser


# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

PI = 3.141592653

display_width, display_height = 64, 32

screen_scale = 9        # scale the Pygame display

screen_status_h = 96    # status field height

app_display_width = display_width * screen_scale
app_display_height = display_height * screen_scale + screen_status_h
app_display_pixels_count = app_display_width * app_display_height

app_display_size = (app_display_width, app_display_height)
#app_screen = pygame.display.set_mode(app_display_size)
#app_screen = pygame.display.set_mode(app_display_size, pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)

app_screen = pygame.display.set_mode(app_display_size, pygame.HWSURFACE | pygame.DOUBLEBUF )



#flags = pygame.OPENGL | pygame.FULLSCREEN
#app_screen = pygame.display.set_mode(app_display_size, flags, vsync=1)


device_screen_pixels_count = display_width * screen_scale * display_height * screen_scale

#device_pixels_count = (display_width * screen_scale) * (display_height * screen_scale)
#surface = pygame.Surface (app_display_size)


pygame.display.set_caption("CHIP8 Emulator by Plrang Art")

pxarray = pygame.PixelArray(app_screen)
clock = pygame.time.Clock()
pygame.key.set_repeat(2000, 2000)

pygame.key.set_repeat(1, 100)

# CHIP8 definition

# 16 - total number of registers in the CHIP8
REGISTERS_NUM = 0x10




CLS_BG = (128, 128, 128)
COL_FG = (160, 255, 160)

CLS_BG = (100, 200, 100)
COL_FG = (64, 64, 64)

# Sets which keys on the keyboard map to the Chip 8 keys
# STANDARD

# KEY_MAP = {
#     pygame.K_KP0: 0x0,
#     pygame.K_KP1: 0x1,
#     pygame.K_KP2: 0x2,
#     pygame.K_KP3: 0x3,
#     pygame.K_KP4: 0x4,
#     pygame.K_KP5: 0x5,
#     pygame.K_KP6: 0x6,
#     pygame.K_KP7: 0x7,
#     pygame.K_KP8: 0x8,
#     pygame.K_KP9: 0x9,
#     pygame.K_a: 0xA,
#     pygame.K_b: 0xB,
#     pygame.K_c: 0xC,
#     pygame.K_d: 0xD,
#     pygame.K_e: 0xE,
#     pygame.K_f: 0xF
# }

# PC NUM
KEY_MAP = {
    pygame.K_KP0: 0x0,
    pygame.K_KP7: 0x1,
    pygame.K_KP8: 0x2,
    pygame.K_KP9: 0x3,
    pygame.K_KP4: 0x4,
    pygame.K_KP5: 0x5,
    pygame.K_KP6: 0x6,
    pygame.K_KP1: 0x7,
    pygame.K_KP2: 0x8,
    pygame.K_KP3: 0x9,
    pygame.K_a: 0xA,
    pygame.K_b: 0xB,
    pygame.K_c: 0xC,
    pygame.K_d: 0xD,
    pygame.K_e: 0xE,
    pygame.K_f: 0xF
}

key_down = 0


print(KEY_MAP)


# MAKE KEYBOARD KEYS DELAY WITH TIME, not to rely on ket up
# Seems to not make things any better

KBOARD_PRESSED_DELAY_DEFAULT = 50
KBOARD_PRESSED_DELAY = {}

for k in KEY_MAP:
    print(k)
    KBOARD_PRESSED_DELAY[k] = 0

print(KBOARD_PRESSED_DELAY)

#exit()


"""
The chip8 machine has a number of registers.
v0 to v15
These are general 8-bit unsigned arithmetic registers. Regsiters v10 to v15 may also be
referred to as vA to vF. Arithmetic is done in 2s compliment

v15 In addition to being a general register, this register may sometimes be used as an
exception indicator by some opcodes.

. The dot register may be used to refer to the value of the program counter maintained by
the assembler. It refers to the value of the program counter before the opcode is
generated.
"""


class chip8CPU(object):

    def __init__(self):

                        # Programs may also refer to a group of sprites representing the hexadecimal digits
                        # 0 through F. These sprites are 5 bytes long, or 8x5 pixels.
                        # The data should be stored in the interpreter area
                        # of Chip-8 memory (0x000 to 0x1FF).
                        # Below is a listing of each character's bytes, in binary and hexadecimal

        self.fontset = [0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
                        0x20, 0x60, 0x20, 0x20, 0x70,  # 1
                        0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
                        0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
                        0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
                        0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
                        0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
                        0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
                        0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
                        0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
                        0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
                        0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
                        0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
                        0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
                        0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
                        0xF0, 0x80, 0xF0, 0x80, 0x80]  # F

    def initialize(self):
        logger.warn('chip8CPU initialize')

        seed()

        # The stack pointer (SP) can be 8-bit, it is used to point to the topmost level of the stack
        self.SP = 0
        #self.SP = 0x052

        # The stack is only used to store return addresses when subroutines are called.
        self.stack = [0]*16
        # The original 1802 version allocated 48 bytes for up to 12 levels of nesting;
        # modern implementations normally have at least 16 levels

        # Stack: only used to store return addresses when subroutines are called.
        # The stack is not stored in memory, but in form of a 16-element array of 16-bit values,
        # storing return addresses. This limits Chip8 to a callstack depth of 16.

        self.opcode = 0

        self.opc_mnemo = ''        # set current opcode decoded to ASM
        # our private asm instruction representation
        self.opcode_asm = ['']*6

        self.memory = bytearray([0] * 4096)

        # PROGRAM COUNTER
        self.PC = 0x200     # When the chip8 machine is reset, the PC is set to 0x200,
        # thus chip8 programs start at 0x200
        # The program counter (PC) should be 16-bit, and is used to store the currently executing address

        self.I = 0          # This register is a pointer register. It is 16-bits long,
        # although the address space is only 12-bits.
        # It is an error to attempt to reference memory above 0xFFF.
        # This register is generally used to store memory addresses,
        # so only the lowest (rightmost) 12 bits are usually used

        # The value of the I register after save and restore opcodes is not well defined. Some emulator
        # leaves the I register pointing past the last location referenced, other emulators leave it pointing at
        # the first location referenced. Defensive programming should assume the I register is not
        # meaningful after these opcodes. (This distribution is consistent with Gustafssons emulator,
        # which moves the I register past the last location referenced.)

        self.V = bytearray([0] * 16)
        # The VF (last one) register should not be used by any program, as it is used as a
        # CARRY FLAG by some instructions

        # WHERE IS IT ???
        # The Borrow Flag ?
        # Many emulators calculate the borrow after the sub and dif opcodes incorrectly. Defensive
        # programming should assume the v15 register is not meaningful after these opcodes. (This
        # distribution is consistent with Gustafssons emulator, which performs the operation in more than
        # 8 bits, and sets the v15 register to 1 if any of the high bits of the result are non-zero, otherwise
        # sets it to 0)

        # Init clear screen
        # self.VRAM = bytearray([0] * 4096)           # this is memory[0xF00];

        self.VRAM = bytearray([0] * (display_width * display_height))

        # This isnt really a register, even though the opcode treat it that way.
        self.KBOARD = [0]*16
        # There are 16 keys available, labeled "0" to "F". Keys may be sampled or waited for

        # Python timer
        self.t_last = time()

        # Fontset
        # for i in range(80):
        #    self.memory[i] = self.fontset[i]

        # THATS BETTER
        self.memory[:80] = bytearray(self.fontset)

        logger.warn('chip8CPU FONTS loaded...')

        # TIMERS

        # When these registers are non-zero, they are automatically decremented at a rate of 60Hz
        # delay_timer should be 8 bit
        # The time register is a count-down timer. It is decrimented by 1 every 60th of a second until it reaches 0.
        self.time = 0

        # sound_timer should be 8 bit
        # The time register is a count-down timer. It is decrimented by 1 every 60th of a second until it reaches 0.
        # If the register is not 0, a beeper will be beeping. (Some implementations make the beeping optional.)
        self.tone = 0

        self.draw_flag = False

        self.ROMloaded = ''
        self.cycle_num = 0

        logger.warn('chip8CPU REGISTERS set...')

    def ROMload(self, filename=''):
        logger.warn('chip8CPU ROM loading... ' + filename)

        fhand = open(filename, 'rb')
        ROMfile = fhand.read()
#       ROMfile = bytearray(ROMfile)

        self.PC = 0x200

        # beautiful one - yet need to check later if those bytes are really bytes ;)
        self.memory[self.PC: len(ROMfile)] = bytearray(ROMfile)

        # instead of primitive one "byte" transfers
#         idx = 0
#         for byte in ROMfile:
#             self.memory[self.PC + idx] = byte & 0xFF
#             idx += 1
        #print byte

        fhand.close()
        logger.warn('Done')

        # MEM DUMP
        #print self.memory
        # sleep(10)

        self.ROMloaded = filename.split('/')[1]

        # return ROM

    def __str__(self):

        #print repr(self.stack)

        if CONSOLE_DEBUG_SCREEN:
            response = "\n*** chip8CPU object state: REGISTERS *** PLRANG *** \n\n\t"
            response += "STACK: \t\t" + str(repr(self.stack)) + "\n\n\t"
            response += "OPCOD: \t\t" + \
                str(hex(self.opcode)) + "\t" + str(self.opcode) + \
                '\t' + self.opcode_asm[0] + "\n\t"
            response += "DISASM HIST: \t\t\t" + self.opcode_asm[1] + "\n\t"
            response += "DISASM HIST: \t\t\t" + self.opcode_asm[2] + "\n\t"
            response += "DISASM HIST: \t\t\t" + self.opcode_asm[3] + "\n\t"
            response += "DISASM HIST: \t\t\t" + self.opcode_asm[4] + "\n\n\t"

            tmp = ''
            for i in range(len(self.memory[0x200: 0x200+30])):
                tmp += format(self.memory[0x200+i], '02x') + ' '

            response += "MEM: \t\t" + str(tmp) + "\n\t"

            response += "PC: \t\t" + str(self.PC) + "\n\t"
            response += "I: \t\t" + str(self.I) + "\n\t"
            response += "SP: \t\t" + str(self.SP) + "\n\t"

            tmp = ''
            for i in range(len(self.V)):
                tmp += format(self.V[i], '02x') + ' '

            response += "V: \t\t" + \
                str(tmp) + ' len:' + str(len(self.V)) + "\n\t"

            response += "KEY: \t\t" + str(key_down) + "\n\t"

            if key_down in KEY_MAP:
                response += "KEY E: \t\t" + str(KEY_MAP[key_down]) + "\n\t"

            #response += "VRAM: \t\t" + repr(self.VRAM[300:340]) + "\n\t"

            tmp = ''
            for i in range(len(self.VRAM[0:30])):
                tmp += format(self.VRAM[0+i], '02x') + ' '

            response += "VRAM: \t\t" + str(tmp) + "\n\t"

            response += "KB_BUF: \t" + str(repr(self.KBOARD)) + "\n\t"
            response += "FONTS: \t\t" + "pass" + "\n\t"
            response += "TIME: \t\t" + str(self.time) + "\n\t"
            response += "TONE: \t\t" + str(self.tone) + "\n\t"

            response += "\n*** chip8CPU object state: OTHER ***\n\n\t"
            response += "Python time: " + str(self.t_last) + "\n\t"
            response += "Draw flag: " + str(self.draw_flag) + "\t\t"
            response += "ROM loaded: " + self.ROMloaded + "\t\t"
            response += "Cycle num: \t" + \
                str(self.cycle_num) + "\t" + "FPS: " + str(FPS)
        else:
            response = ''


        # DISPLAY VRAM in CONSOLE - for testing

        if TEST_VRAM:
            response = ''
            count_w = 1
            vram_len = 0
            line_store = ''

            print("\033[1;1f")


            # TODO: optimize it

            for pixel in self.VRAM:
                #response += str(pixel)

                if not pixel:
                    pixOff = ' ' * screen_scale
                    response += pixOff
                    line_store += pixOff
                else:
                    pixOn = chr(219) * screen_scale
                    response += pixOn
                    line_store += pixOn


                #if count_w % display_width == 0:
                if count_w * screen_scale % app_display_width == 0:
                    response += '\n'
                    line_store += '\n'
                    line_store = line_store * (screen_scale -1)

                    response += line_store
                    count_w = 0

                    line_store = ''



                count_w += 1
                vram_len += 1

                if vram_len > display_width * display_height:
                    vram_len = 0
                    break


        if CONSOLE_DEBUG_MSG:
            response =  str(self.cycle_num) + ' OP:' + str(hex(self.opcode)) + ' : ' + self.opc_mnemo

        return response



    # RUN CYCLE

    def RUNcycle(self):

        # Decode & Execute

        asm = self.OPCdecode()

        # TIMERS update

        if self.tone > 0:
            #print '\a'

            #winsound.Beep(7000 - self.tone * 200, 5)

            self.tone -= 1

        # Allow to ADJUST the DELAY TIMER according to the "clock"
        if self.cycle_num%10==0:
            if self.time > 0:
                self.time -= 1

            # Program Counter UP

            # CHECK ??????????????????????????
            # ON OR OFF ???

            #self.I = self.opcode & 0x0FFF

        # keep the limit of our private ASM command list

        # if self.cycle_num==1:
        self.opcode_asm.insert(0, asm)
        self.opcode_asm.pop()

        # CHIP STATE OBJ SHOW

        self.PC += 2
        self.cycle_num += 1     # just for us


    # OPCODEs DECODE & EXECUTE

    def OPCdecode(self):
        # OPCODE Load
        #     merge both bytes and store them in an unsigned short (2 bytes datatype)
        #     then use the bitwise OR operation

        # EXTRACT operands and data    http://devernay.free.fr/hacks/chip8/C8TECH10.HTM#1.0

        self.opcode = (self.memory[self.PC] << 8) | self.memory[self.PC + 1]

        # alt. BISQWIT code https://bisqwit.iki.fi/jutut/kuvat/programming_examples/chip8/
        #self.opcode = self.memory[ self.PC & 0xFFF ] *0x100 + self.memory[ (self.PC + 1) & 0xFFF ]

        # move it right to fit the V index
        self.X = ((self.opcode & 0x0F00) >> 8) & 0xF
        self.Y = ((self.opcode & 0x00F0) >> 4) & 0xF
        self.n = self.opcode & 0x000F
        self.nn = self.opcode & 0x00FF
        self.nnn = self.opcode & 0x0FFF

        if CONSOLE_DEBUG_MSG:
            print str(self.cycle_num) + ' PC:' + str(hex(self.PC))

        self.opcode_lookup = {

            # 0 based opcodes for Clear screen, RTS and Calls RCA 1802 program at address NNN. Not necessary for most ROMs.
            0x0000: self.op_CLS_RET_RCA_1802,
            0x00E0: self.op_cls,                   # Clear VRAM
            0x00EE: self.op_RTS,                   # Return From Subroutine

            0x1000: self.op_JMP,                   # 1nnn JMP to nnn
            # 2nnn call SUBroutine at nnn. STORE STACK[++SP] = PC & PC = nn
            0x2000: self.op_SUB,

            0x3000: self.op_SE_vx_nn,              # 3Xnn SKIP next if VX == nn
            0x4000: self.op_SNE_vx_nn,             # 4Xnn SKIP next if VX != nn

            0x5000: self.op_SE_vx_vy,              # 5Xnn SKIP next if VX == VY

            0x6000: self.op_LD_vx_nn,              # 6Xnn    to VX load nn
            0x7000: self.op_ADD_vx_nn,             # 7Xnn    to VX add nn

            0x8000: self.op_LD_vx_vy,              # 8XY0    to VX load VY

            # 8XY1    to VX load (VX or | VY)
            0x8001: self.op_LD_vx_vx_or_vy,
            # 8XY2    to VX load (VX and & VY)
            0x8002: self.op_LD_vx_vx_and_vy,
            # 8XY3    to VX load (VX xor ^ VY)
            0x8003: self.op_LD_vx_vx_xor_vy,
            # 8XY4    to VX add VY - if Carry , set  vF to 1, else 0
            0x8004: self.op_LD_vx_vx_add_vy,
            # 8XY5    to VX sub VY - VF is set to 0 when there's a borrow, and 1 when there isn't
            0x8005: self.op_LD_vx_vx_sub_vy,
            # 8XY6    shift VX right by 1.     VF is set to value of
            0x8006: self.op_SHR_vx,
            #         least significant bit of VX before the shift

            # 8XY7    set VX to VY minus VX.
            0x8007: self.op_SUBn_vx_vy,
            #         VF is set to 0 when there's a borrow, and 1 when there isn't.

            # 8XYE    Shifts VX left by one.
            0x800E: self.op_SHL_vx,
            #         VF is set to the value of the most significant bit of VX before the shift.

            0x9000: self.op_SNE_vx_vy,             # 9XY0    skips next instruction if VX != VY


            # Annn    ld I, nnn  - Annn - Sets I to the address nnn
            0xA000: self.op_LOAD_I_nnn,

            0xB000: self.op_JP_v0_nnn,              # Bnnn    JUMP to nnn + V0

            # CXnn    VX = result of '&' on random number and NN
            0xC000: self.op_RND_vx_nn,


            0xD000: self.op_D_XYN,                  # Dxyn    DRAW

            # Ex9E    skip next instruction if key stored in VX is pressed
            0xE09E: self.op_SKP_vx,
            # ExA1    skip next instruction if key stored in VX is NOT pressed
            0xE0A1: self.op_SKNP_vx,


            0xF007: self.op_LD_VX_dt,               # Fx07     VX = self.time

            # Fx0A    Wait for a key press, store the value of the key in Vx.
            0xF00A: self.op_LD_VX_n,
            #         All execution stops until a key is pressed,
            #         then the value of that key is stored in Vx

            # Fx15     self.time = VX    - delay timer set to VX
            0xF015: self.op_LD_dt_VX,
            # Fx18     self.tune = VX    - sound timer set to VX
            0xF018: self.op_LD_st_VX,
            0xF01E: self.op_ADD_i_VX,               # Fx1E     to I add VX


            # Fx29      Set I = location of sprite for digit Vx
            0xF029: self.op_LD_f_VX,
            #             The value of I is set to the location for the hexadecimal sprite corresponding to the value of Vx
            # Fx33      store BCD representation of Vx in memory locations I, I+1, and I+2
            0xF033: self.op_LD_b_VX,
            #               The interpreter takes the decimal value of Vx, and places the hundreds digit in memory at location in I,
            #               the tens digit at location I+1,
            #               and the ones digit at location I+2

            # Fx55        put registers V0 - Vx in memory at location I >
            0xF055: self.op_LD_i_VX,

            # Fx65        Fills V0 to VX (including VX) with values from memory starting at address I
            #             fill V0 to VX with contents of mem[I]+

            0xF065: self.op_LD_VX_i


        }

        op_test = self.opcode & 0xF000


        # TEST - looking for this opcode if it does work?
        #if op_test == 0xb000:
        #    winsound.Beep(Freq, 50)

        switch = {
            0x0000: lambda: 0x0000 | self.opcode & 0xF0FF,  # important first F as a op type and last F as a op number
            0x8000: lambda: 0x8000 | self.opcode & 0xF00F,  # like 0x8XY1
            0xE000: lambda: 0xE000 | self.opcode & 0xF0FF,  # if op_code is like 0xFzzz then opcodes are 0xFX12,
            0xF000: lambda: 0xF000 | self.opcode & 0xF0FF   # so make the OR with F0 and FF to clear the data at 0
        }

        if op_test in switch:
            #print 'lookup::: ', hex(switch[op_test]())
            lookup = switch[op_test]()

        else:   # found direct opcode, no need for switching
            lookup = self.opcode & 0xF000

        # else:
        #lookup = self.opcode & 0xF000

        try:
            # run the choosen procedure
            self.opcode_lookup[lookup]()

            return str(hex(self.opcode)) + '\t' + self.opc_mnemo
        except KeyError:
            return str(hex(self.opcode)) + ' Look up error'
            pass














    # ***************
    # *** OPCODES ***
    # ***************

    # 0x0000

    def op_CLS_RET_RCA_1802(self):

        #self.PC = self.nnn
        self.opc_mnemo = 'unused RCA 1802 ' + str(hex(self.opcode))

    # 0x00E0                                clear screen

    def op_cls(self):

        for i in range(len(self.VRAM)):
            self.VRAM[i] = 0


        # pxarray[:,:] = (128,0,0)#CLS_BG
        #pxarray[:,:] = CLS_BG
        # clean only the "device" screen part - not the status area below

        if PYGAME_DISPLAY:
            pxarray[:display_width * screen_scale,
                    :display_height * screen_scale] = CLS_BG

        self.opc_mnemo = "CLS"

    # 0x00EE                                return from a subroutine
    def op_RTS(self):

        self.SP -= 1
        self.PC = self.stack[self.SP % 16]

        self.opc_mnemo = "RTS"

    # 0x1nnn                                jump to address NNN

    def op_JMP(self):

        self.PC = self.nnn

        self.opc_mnemo = "JP " + str(hex(self.nnn))
        self.PC -= 2                        # HAD TO REMOVE one cycle otherwise it jumped too far
        # there is a single increment instruction in the main loop
        # self.PC += 2
        # so there is no need to repeat it in every other procedure

    # 0x2nnn                                    call a SUBroutine at nnn. STORE STACK[++SP] = PC & PC = nnn
    def op_SUB(self):                           # TODO check for ++self.SP % 12 - at BISKWIT

        # increment stack pointer SP + 1 and put there current PC / program counter on the stack
        self.stack[self.SP % 16] = self.PC
        self.SP += 1

        self.PC = self.nnn                      # new program counter PC
        self.PC -= 2

        self.opc_mnemo = "SUB ~ call " + str(hex(self.nnn))

    # 3Xnn              skip the next instruction if VX == NN

    def op_SE_vx_nn(self):
        X = self.X

        if self.nn == self.V[X]:
            self.PC += 2

        self.opc_mnemo = "SE V" + str(X) + ', ' + str(self.nn)

    # 4Xnn                                 skip the next instruction if VX != NN

    def op_SNE_vx_nn(self):
        X = self.X

        if self.V[X] != self.nn:
            self.PC += 2

        self.opc_mnemo = "SNE VX " + \
            str(X) + ", " + str(hex(self.nn)) + " = nn"

    # 5XY0                                  skip the next instruction if VX == VY

    def op_SE_vx_vy(self):
        X = self.X
        Y = self.Y

        if self.V[X] == self.V[Y]:
            self.PC += 2

        self.opc_mnemo = "SE V" + \
            str(X) + " = " + str(hex(self.V[X])) + \
            ", V" + str(Y) + " = " + str(hex(self.V[Y]))

    # 6Xnn                                        LD set VX to NN

    def op_LD_vx_nn(self):
        X = self.X

        self.V[X] = self.nn

        self.opc_mnemo = "LD V" + str(X) + ", " + str(hex(self.nn))

    # 7Xnn                                        to VX add nn

    def op_ADD_vx_nn(self):
        X = self.X

        self.V[X] = (self.V[X] + self.nn) & 0xFF  # need to take care of BYTES
        #self.V[X] = (self.V[X] + self.nn) % 256

        self.opc_mnemo = "ADD V" + \
            str(X) + ", " + str(self.V[X]) + ", " + str(self.nn)


    # 8XY0                                           set to VX load VY

    def op_LD_vx_vy(self):
        X = self.X
        Y = self.Y

        self.V[X] = self.V[Y]

        self.opc_mnemo = "LD V" + str(X) + ", " + "V" + str(Y)

    # 8XY1                                            or vX,vY    VX = VX or VY
    def op_LD_vx_vx_or_vy(self):
        X = self.X
        Y = self.Y

        self.V[X] = (self.V[X] | self.V[Y]) & 0xFF  # byte

        self.opc_mnemo = "or V" + str(X) + ", " + "V" + str(Y)

    # 8XY2                                            to VX load (VX and & VY)

    def op_LD_vx_vx_and_vy(self):
        X = self.X
        Y = self.Y

        self.V[X] = (self.V[X] & self.V[Y]) & 0xFF      # byte

        self.opc_mnemo = "and V" + str(X) + ", " + "V" + str(Y)

    # 8XY3                                            to VX load (VX xor ^ VY)

    def op_LD_vx_vx_xor_vy(self):
        X = self.X
        Y = self.Y

        # byte       # xor vX,vY    VX = VX ^ VY
        self.V[X] = (self.V[X] ^ self.V[Y]) & 0xFF

        self.opc_mnemo = "xor V" + str(X) + ", " + "V" + str(Y)

    # 8XY4                                        to VX add VY - if Carry , set  vF to 1, else 0

    def op_LD_vx_vx_add_vy(self):
        X = self.X
        Y = self.Y

        val = self.V[X] + self.V[Y]
        if val > 255:
            self.V[0xF] = 0x1  # (val >> 8) & 0xff
        else:
            self.V[0xF] = 0x0

        self.V[X] = val & 0xFF
        #self.V[X] %= 256

        self.opc_mnemo = "add V" + \
            str(X) + ", " + "V" + str(Y) + ' carry: ' + str(self.V[0xF])

    # 8XY5                                        VX =  VX sub VY ; VF is set to 0 when there's a borrow, and 1 when there isn't

    def op_LD_vx_vx_sub_vy(self):
        X = self.X
        Y = self.Y

        val = self.V[X] - self.V[Y]

        if self.V[X] > self.V[Y]:
            self.V[0xF] = 0x1
        else:
            self.V[0xF] = 0x0

        #self.V[X] = val % 256
        self.V[X] = val & 0xFF              # take care of BYTES
        # self.V[0xF] = (~(val >> 8)) & 0xFF
        # something is not right here wven with ~

        self.opc_mnemo = "sub V" + \
            str(X) + ", " + "V" + str(Y) + ' carry: ' + str(self.V[0xF])

    # 8XY7    set VX to VY minus VX.
    #         VF is set to 0 when there's a borrow, and 1 when there isn't.

    def op_SUBn_vx_vy(self):
        X = self.X
        Y = self.Y

        val = self.V[Y] - self.V[X]

        if self.V[Y] > self.V[X]:
            self.V[0xF] = 0x1
        else:
            self.V[0xF] = 0x0

        self.V[X] = val & 0xFF              # take care of BYTES

        self.opc_mnemo = "subn V" + \
            str(X) + ", " + "V" + str(Y) + ' VF borrow: ' + str(self.V[0xF])

    # 8XY6                 shift VX right by 1.     VF is set to value of
    #                      least significant bit of VX before the shift

    def op_SHR_vx(self):
        X = self.X
        Y = self.Y

        self.V[0xF] = self.V[X] & 0x01
        self.V[X] = (self.V[X] >> 1) & 0xFF

        self.opc_mnemo = "shr V" + str(X) + " >>1"

    # 8XYE                shift VX left by one.
    #                     VF is set to the value of the most significant bit of VX before the shift.
    def op_SHL_vx(self):
        X = self.X
        Y = self.Y

        self.V[0xF] = (self.V[X] >> 7) & 0x01
        self.V[X] = (self.V[X] << 1) & 0xFF

        self.opc_mnemo = "shl V" + str(X) + " <<1"

    # 0x9000                9XY0    skips next instruction if VX != VY

    def op_SNE_vx_vy(self):
        X = self.X
        Y = self.Y

        if self.V[X] != self.V[Y]:
            self.PC += 2

        self.opc_mnemo = "SNE V" + \
            str(X) + '('+str(hex(X)) + ')' + ", V" + \
            str(Y) + '('+str(hex(Y)) + ')'

    # Annn                            sets I to the address NNN.

    def op_LOAD_I_nnn(self):

        self.I = self.nnn

        self.opc_mnemo = "LD I, " + str(hex(self.I))

    # Bnnn                            JUMP to nnn + V0

    def op_JP_v0_nnn(self):

        self.PC = self.nnn + self.V[0]
        self.PC -= 2

        self.opc_mnemo = "JP V0 " + ", " + \
            str(hex(self.PC)) + ' PC=(' + \
            str(hex(self.V[0])) + ' + ' + str(hex(self.nnn)) + ')'

    # 0xC000                            CXnn    VX = result of '&' on random number and NN

    def op_RND_vx_nn(self):
        X = self.X
        nn = self.nn

        self.V[X] = (randint(0, 255) & nn) & 0xFF  # byte

        self.opc_mnemo = "rnd VX " + str(hex(X)) + ", " + str(hex(nn))

# Dxyn    DRAW
#    Display n-byte sprite starting at memory location I at (Vx, Vy),
#    set VF = collision. The interpreter reads n bytes from memory,
#    starting at the address stored in I.
#    These bytes are then displayed as sprites on screen at coordinates (Vx, Vy).

#    Sprites are XOR'd onto the existing screen.
#    If this causes any pixels to be erased, VF is set to 1, otherwise it is set to 0.
#    If the sprite is positioned so part of it is outside the coordinates of # the display,
#    it wraps around to the opposite side of the screen

# TODO: move the drawing code - not related to the emulator architecture - to an external procedure
# for easier reading and optimalization

    def op_D_XYN(self):                       # Dxyn    DRAW

        X = self.V[self.X]
        Y = self.V[self.Y]
        n = self.n

        self.V[0xF] = 0

        for next_pix in range(n):
            pixel = self.memory[self.I + next_pix]

            for x_line in range(8):           # 8 bits per line
                #x_coord = X % display_width + x_row * 8

                x_pos = (X + x_line) % display_width
                y_pos = (Y + next_pix) % display_height

                sprite_bit = (pixel >> (7 - x_line)) & 1

                bit_pos = y_pos * display_width + x_pos
                VRAM_old = self.VRAM[bit_pos]

                self.VRAM[bit_pos] = VRAM_old ^ sprite_bit

                if VRAM_old != 0 and self.VRAM[bit_pos] == 0:
                    self.V[0xF] = 1

                new_x = x_pos * screen_scale
                new_y = y_pos * screen_scale

                if VRAM_old ^ sprite_bit:
                    if PYGAME_DISPLAY:
                        pxarray[new_x: new_x + screen_scale,
                                new_y: new_y + screen_scale] = COL_FG
                else:
                    if self.V[0xF]:
                        if PYGAME_DISPLAY:
                            pxarray[new_x: new_x + screen_scale,
                                    new_y: new_y + screen_scale] = CLS_BG


#                if pixel & (0x80 >> x_line) != 0:
#                     if self.VRAM[ X + x_line + (Y + y_line) * 64 ] == 1 :
#                         self.V[0xF] = 1
#                         self.VRAM[ X + x_line + (Y + y_line) * 64 ] ^= 1

                #print X, Y

        self.draw_flag = True

        # theoretically in the VRAM

        # if self.VRAM[ y_coord * display_width + x_coord ]
        #self.VRAM[ y_coord * display_width + x_coord ] = 1

        self.opc_mnemo = "DRW " + str(X) + ' ' + str(Y) + ' ' + str(n)

    # 0xE09E                                    # Ex9E    skip next instruction if key stored in  VX  is pressed

    def op_SKP_vx(self):
        X = self.X

        if self.KBOARD[self.V[X] & 0xF] == 1:
            self.PC += 2


        self.opc_mnemo = "SKP_vx"

    # 0xE0A1                                    # ExA1    skip next instruction if key stored in  VX  is NOT pressed

    def op_SKNP_vx(self):
        X = self.X

        if self.KBOARD[self.V[X] & 0xF] != 1:
            self.PC += 2


        self.opc_mnemo = "SKNP_vx"

    # Fx07                                            VX = self.time
    # DELAY TIMER to VX

    def op_LD_VX_dt(self):
        X = self.X
        self.V[X] = self.time

        self.opc_mnemo = "LD V" + str(X) + ', ' + str(self.time)

    # 0xF00A                                    Fx0A    Wait for a key press, store the value of the key in Vx.
        #       All execution stops until a key is pressed (?)
        #       then the value of that key is stored in Vx

    def op_LD_VX_n(self):
        X = self.X

        if key_down:
            self.KBOARD[KEY_MAP[key_down]] = 1      #
            # the REQUIRED signal comes from the keyboard pressed
            self.V[X] = KEY_MAP[key_down]
        # else:
        #     self.PC -= 2


    # Fx18                                          self.tone = VX    - sound timer set to VX
    # VX to SOUND TIMER

    def op_LD_st_VX(self):
        X = self.X

        self.tone = self.V[X]
        self.opc_mnemo = "LD st, V" + str(X) + " (" + str(hex(self.V[X])) + ")"

    # VX to DELAY TIMER
    # Fx15    self.time = VX    - delay timer set to VX

    def op_LD_dt_VX(self):
        X = self.X

        self.time = self.V[X]
        self.opc_mnemo = "LD dt, V" + str(X) + " (" + str(hex(self.V[X])) + ")"

    # I + VX
    # Fx1E      to I add VX

    def op_ADD_i_VX(self):
        X = self.X

        self.I = (self.I & 0xFFF) + self.V[X]
        self.V[0xF] = self.I >> 12

        self.opc_mnemo = "ADD I, V" + str(X) + ', ' + str(hex(self.V[X]))

    # Fx29                                      Set I = location of sprite for digit Vx

    def op_LD_f_VX(self):
        X = self.X
        #    & 0xFF may be unnecessary - just checking
        # The value of I is set to the location
        self.I = (self.V[X] & 0xFF) * 5
        #    for the hexadecimal sprite
        #    corresponding to the value of Vx
        self.opc_mnemo = "LD f, V" + str(X) + ' (' + (str(self.I)) + ')'

    # Fx33
    # BCD representation of Vx put to I (hundreds), I+1 (tens) and I+2 (ones)

    def op_LD_b_VX(self):
        X = self.X
        VX = self.V[X]

        self.memory[self.I & 0xFFF] = ((VX / 100) % 10) & 0xFF
        self.memory[(self.I + 1) & 0xFFF] = ((VX / 10) % 10) & 0xFF
        self.memory[(self.I + 2) & 0xFFF] = ((VX / 1) % 10) & 0xFF

        self.opc_mnemo = "LD B, V" + str(X) + ' (' + (str(hex(VX))) + ')'

    # Fx55
    # V0 to VX put at mem[I]

    def op_LD_i_VX(self):
        X = self.X

        for i in range(X + 1):
            self.memory[(self.I + i) & 0xFFF] = self.V[i]

        self.opc_mnemo = 'LD memI[' + \
            str(hex(self.I)) + ']+' + ", V 0-" + str(hex(X))

    # Fx65                                        Fills V0 to VX (including VX) with values from memory starting at address I
    #                                             fill V0 to VX with contents of mem[I]+

    def op_LD_VX_i(self):
        X = self.X

        self.opc_mnemo = "LD V 0-" + \
            str(hex(X)) + ', memI[' + str(hex(self.I)) + ']+'

        for i in range(X + 1):
            self.V[i] = self.memory[(self.I + i) & 0xFFF]






# START the action
# CREATE the CPU

chip8CPU = chip8CPU()

# Initialize the system and load the game

chip8CPU.initialize()

# Force this ROM to load as first - supply a specific ROM filename
#

# ROM_filename = "ROMs/Tetris.ch8"
# ROM_filename = "ROMs/Trip8.ch8"
#ROM_filename = "ROMs/DelayTimerTest.ch8"

chip8CPU.ROMload(ROM_filename)

logger.warn('chip8CPU start...')

#print '\a'

winsound.Beep(Freq, Dur)
print("\033[2J\033[1;1f")    # CLS
pxarray[:, :] = CLS_BG       # CLS pygame



# MAIN LOOP as long as done == False
done = False
#ROM_index = 0
status_printing = True


tmp_timer_delay = 0





def status_print():
    global status_printing, KBOARD_PRESSED_DELAY

    font = pygame.font.SysFont('Small Fonts', 28, False, False)

    if FPS == 0:
        text = font.render("Clock: " + "unlimited", True, COL_FG)
    else:
        text = font.render("Clock: " + str(FPS), True, COL_FG)

    if PYGAME_DISPLAY:
        app_screen.blit(text, [8, app_display_height - 60])

        text = font.render("ROM up / dn: " + chip8CPU.ROMloaded, True, COL_FG)
        app_screen.blit(text, [180, app_display_height - 60])
        status_printing = False





# Variables to hold values needed for setting the requested FPS rate
# not used yet

time_passed = 0
lastTime = 0
FPSrequired = 10

while not done:

    # Virtual screen array
    if PYGAME_DISPLAY:
        pxarray = pygame.PixelArray(app_screen)


    for event in pygame.event.get():  # User did something

        if event.type == pygame.QUIT:  # If user clicked close
            done = True  # Flag that we are done so we exit this loop



#    STEP BY STEP control part 1

#         if event.type != pygame.KEYDOWN:
#             do_continue = True
#         else:
#             key_down = event.key
#             if key_down == K_SPACE:
#                 do_continue = False

        if event.type == pygame.KEYDOWN:
            #key_down = pygame.key.get_pressed()
            key_down = event.key
            if key_down in KEY_MAP:
                #chip8CPU.KBOARD[KEY_MAP[key_down]] = 1
                chip8CPU.KBOARD[KEY_MAP[key_down]] = 1

                KBOARD_PRESSED_DELAY[ key_down ] = KBOARD_PRESSED_DELAY_DEFAULT

            if key_down == pygame.K_ESCAPE:
                quit()

            # ROM SWITCHING
            if key_down == pygame.K_UP:
                ROM_index += 1
                if ROM_index > len(ROMs) - 1:
                    ROM_index = 0

            if key_down == pygame.K_DOWN:
                ROM_index -= 1
                if ROM_index < 0:
                    ROM_index = len(ROMs) - 1

            if key_down == pygame.K_DOWN or key_down == pygame.K_UP:

                print("\033[2J\033[1;1f")   # CLS

                if PYGAME_DISPLAY:
                    pxarray[:, :] = CLS_BG      # CLS pygame

                ROM_filename = ROMs.keys()[ROM_index]
                ROM_FPS = ROMs.values()[ROM_index]
                FPS = ROM_FPS


                chip8CPU.initialize()
                chip8CPU.ROMload(ROM_filename)
                status_printing = True
                #print ROM_index

        else:

            # chip8CPU.KBOARD = [0]*16
            # key_down = False

# **************** THIS BLOCK instead of above 2 lines - to create a delayable keyboard input
# to see if in SPACE INVADERS the ship will move faster / possibly dropped key presses?
# SEEMS like it doesn't do any better
#
#
            pass

    for index, v in enumerate(KBOARD_PRESSED_DELAY):
        #print(index, v, KEY_MAP[v])
        if KBOARD_PRESSED_DELAY[ v ] > 0:
            KBOARD_PRESSED_DELAY[ v ] -=1

        if KBOARD_PRESSED_DELAY[ v ] == 0:

            chip8CPU.KBOARD[ KEY_MAP[v] ] = 0   # clear the CHIP8 keyboard buffer after a given delay
            KBOARD_PRESSED_DELAY[ v ] = -1


    #print(KBOARD_PRESSED_DELAY)


    #print(chip8CPU.KBOARD)  # TESTING


# **************** THIS BLOCK


#    STEP BY STEP control part 2
    # FPS = 1456123525245621
#         if do_continue: continue

    #print "now:", now
    #elapsed =  now - lastTime

    #print "lastTime:", lastTime
    #print "Elapsed: ", elapsed

    #deltaTime = elapsed /1000


    # Control FPS if not 0
    #FPS = 800

    if FPS!=0:
        deltaTime = clock.tick(FPS)
        #clock.tick_busy_loop(FPS)


    #print "Delta T:", deltaTime


    # if deltaTime < 0.0001:
    #     deltaTime = 0.0001

    FPSrequired = 60
    #FPScurrent = 1/ float(deltaTime)
    time_passed += deltaTime

    #print "time_passed:", time_passed
    # print "float(time_passed)/100:", float(time_passed)/100


    #print "FPSrequired:", FPSrequired
    # print "1/FPSrequired:", 1/float(FPSrequired)


    # DO a CPU CYCLE

    # UPCYCLE loop for more emulator ticks in a main loop - increase the performance
    for k in range(2):
        if CONSOLE_CLS:
            # USED for that F... screen CLEAR!
            # different ways to clear the console
            print("\033[2J\033[1;1f")         # this instr. instead of the one below worked better on Win 8
                                                # try to uncomment it and comment the one below [] os.system('cls') ], to compare
            # os.system('cls')        # for Windows
            # os.system('clear')    # for Linux/OS X

        chip8CPU.RUNcycle()

    #if float(time_passed)/1000 > 1/float(FPSrequired):


        #chip8CPU.RUNcycle()

        #print "time_passed:", float(time_passed)/1000
        # print "1/float(FPSrequired):", 1/float(FPSrequired)


        #time_passed = 0
        # print "CYCLE = 1"
    # else:
        # print "CYCLE = 0"




    # Virtual screen array remove and update the view
    if PYGAME_DISPLAY:
        del pxarray

    if status_printing:
        status_print()

    #if tmp_timer_delay == 2:

    if PYGAME_DISPLAY:
        pygame.display.update()

        #tmp_timer_delay=0

    #tmp_timer_delay += 1


    #lastTime = now



# Be IDLE friendly
pygame.quit()

exit()