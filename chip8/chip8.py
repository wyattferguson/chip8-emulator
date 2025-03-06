import argparse

import pygame as pg

from cpu import CPU
from keyboard import Keyboard
from screen import Screen


def run(rom: str = "test.ch8", screen_scale: int = 10) -> None:
    pg.init()
    pg.display.set_caption(f"👾 Chip8 Emulator :: {args.rom} :: {args.scale}x Scale")

    screen = Screen(screen_scale)
    keyboard = Keyboard()
    cpu = CPU(rom, screen, keyboard)

    clock = pg.time.Clock()

    while True:
        clock.tick(60)
        cpu.cycle()
        screen.update()
        keyboard.update()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-r",
        "--rom",
        default="./roms/walk.ch8",
        help="ROM file to run (.ch8 file).",
    )

    parser.add_argument(
        "-s",
        "--scale",
        default="20",
        type=int,
        help="Scale multiplier for the screen size.",
    )

    args = parser.parse_args()
    print(f"👾 Chip8 Emulator Running :: {args.rom} @ {args.scale}x resolution")
    run(args.rom, args.scale)
