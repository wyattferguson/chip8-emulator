import pygame as pg

from chip8.config import (
    BLACK,
    DEFAULT_SCALE,
    WHITE,
)
from chip8.constants import PIXEL_HEIGHT, PIXEL_WIDTH, SCREEN_HEIGHT, SCREEN_WIDTH
from chip8.ctypes import Color, ScreenBuffer


class Screen:
    """Gameplay Screen."""

    def __init__(self, scaler: int = DEFAULT_SCALE) -> None:
        self.scaler = scaler
        self.buffer: ScreenBuffer = self._empty_buffer()  # pixel representation of display
        self.dirty = True  # only push frames when the framebuffer changes

        self.screen = pg.display.set_mode((SCREEN_WIDTH * scaler, SCREEN_HEIGHT * scaler))
        self.clear()

    def flip_pixel(self, x: int = 0, y: int = 0) -> bool:
        """Flip pixel at (x, y) coordinates."""
        # wrap around screen
        x %= SCREEN_WIDTH
        y %= SCREEN_HEIGHT

        self.buffer[y][x] ^= 1
        self.dirty = True

        # was a pixel erased
        return not self.buffer[y][x]

    def _empty_buffer(self) -> ScreenBuffer:
        """Create a blank screen buffer."""
        return [[0 for _ in range(SCREEN_WIDTH)] for _ in range(SCREEN_HEIGHT)]

    def clear(self) -> None:
        """Blank entire screen."""
        self.buffer = self._empty_buffer()
        self.dirty = True

    def draw_pixel(self, x: int, y: int) -> None:
        """Draw a single buffer pixel at (x, y) coordinates."""
        color: Color = WHITE if self.buffer[y][x] else BLACK
        pg.draw.rect(
            self.screen,
            color,
            [
                x * self.scaler,
                y * self.scaler,
                PIXEL_WIDTH * self.scaler,
                PIXEL_HEIGHT * self.scaler,
            ],
        )

    def update(self) -> None:
        """Update entire visible screen."""
        if not self.dirty:
            return

        for y in range(SCREEN_HEIGHT):
            for x in range(SCREEN_WIDTH):
                self.draw_pixel(x, y)
        pg.display.update()
        self.dirty = False
