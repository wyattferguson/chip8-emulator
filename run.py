

from config import ROM_FILE
from cpu import ChipCPU
from screen import ChipScreen


def run():
    screen = ChipScreen()
    cpu = ChipCPU(screen)
    cpu.load_rom(ROM_FILE)

    while True:
        cpu.cycle()
        screen.update()


if __name__ == "__main__":
    run()
