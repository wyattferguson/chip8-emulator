import pygame as pg

from ._config import DEFAULT_ROM, DEFAULT_SCALE, TICK_RATE
from .cpu import CPU
from .keyboard import Keyboard
from .screen import Screen


class Chip8:
    def __init__(
        self, rom: str = DEFAULT_ROM, screen_scale: int = DEFAULT_SCALE, debug: bool = False
    ) -> None:
        self.rom = rom
        self.screen_scale = screen_scale
        self.debug = debug
        self.screen = Screen(self.screen_scale)
        self.keyboard = Keyboard()
        self.cpu = CPU(self.rom, self.screen, self.keyboard)
        self.clock = pg.time.Clock()

    def run(self) -> None:
        pg.init()
        pg.display.set_caption(f"👾 Chip8 Emulator :: {self.rom} :: {self.screen_scale}x Scale")

        while True:
            self.cpu.cycle()
            self.screen.update()
            self.keyboard.update()
