import pygame as pg

from chip8.audio import Audio
from chip8.config import DEFAULT_ROM, DEFAULT_SCALE
from chip8.constants import TICK_RATE
from chip8.cpu import CPU
from chip8.keypad import Keypad
from chip8.ram import RAM
from chip8.screen import Screen


class Chip8:
    """Chip8 Emulator."""

    def __init__(
        self,
        rom: str = DEFAULT_ROM,
        screen_scale: int = DEFAULT_SCALE,
    ) -> None:
        self.rom = rom

        pg.init()
        pg.display.set_caption("👾 Chip8 Emulator")

        self.screen = Screen(screen_scale)
        self.keypad = Keypad()
        self.audio = Audio()
        self.ram = RAM(rom)
        self.cpu = CPU(self.ram, self.screen, self.keypad, self.audio)
        self.clock = pg.time.Clock()

    def run(self) -> None:
        """Run the emulator."""
        while True:
            self.keypad.update()
            self.cpu.cycle()
            self.audio.update()
            self.screen.update()
            self.clock.tick(TICK_RATE)  # Limit to display tick rate
