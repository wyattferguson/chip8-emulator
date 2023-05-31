from pygame import time

from config import DELAY
from cpu import ChipCPU
from screen import ChipScreen


def run():
    rom = "./roms/pong.ch8"
    screen = ChipScreen()
    cpu = ChipCPU(screen)
    cpu.load_rom(rom)

    while True:
        time.wait(DELAY)
        cpu.cycle()
        screen.update()


if __name__ == "__main__":
    run()
