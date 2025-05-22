import pygame as pg

from chip8._config import DEFAULT_ROM, DEFAULT_SCALE
from chip8.cpu import CPU
from chip8.keypad import Keypad
from chip8.screen import Screen


class Chip8:
    """Chip8 Emulator."""

    def __init__(
        self,
        rom: str = DEFAULT_ROM,
        screen_scale: int = DEFAULT_SCALE,
        debug: bool = False,
    ) -> None:
        self.rom = rom
        self.screen_scale = screen_scale
        self.debug = debug
        self.screen = Screen(self.screen_scale)
        self.keypad = Keypad()
        self.cpu = CPU(self.rom, self.screen, self.keypad)
        self.clock = pg.time.Clock()

    def run(self) -> None:
        """Run the emulator."""
        pg.init()
        pg.display.set_caption(f"👾 Chip8 Emulator :: {self.rom} :: {self.screen_scale}x Scale")

        while True:
            self.cpu.cycle()
            self.screen.update()
            self.keypad.update()
