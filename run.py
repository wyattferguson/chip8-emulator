import pygame as pg

DISPLAY_SCALER = 4

ram = [0] * 4000

display_width = 64
display_height = 32

pc = 00 # program counter
loc = 00 # locations register
vf = 00 # flag register
registers = [00000000] * 16 # general purpose registers
stack = []

delay_timer = 00000000
sound_timer = 00000000


def main() -> None:
    pass


if __name__ == "__main__":
    main()