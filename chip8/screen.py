import pygame as pg

from ._config import (
    BLACK,
    DEFAULT_SCALE,
    PIXEL_HEIGHT,
    PIXEL_WIDTH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    WHITE,
)


class Screen:
    """Pygame Screen."""

    matrix: list[list[int]] = []  # pixel representation of display

    def __init__(self, scaler: int = DEFAULT_SCALE) -> None:
        self.sprite_width = PIXEL_WIDTH * scaler
        self.sprite_height = PIXEL_HEIGHT * scaler
        self.scaler = scaler

        self.screen = pg.display.set_mode((SCREEN_WIDTH * scaler, SCREEN_HEIGHT * scaler))
        self.clear()

    def set_pixel(self, x: int = 0, y: int = 0) -> bool:
        x %= SCREEN_WIDTH
        y %= SCREEN_HEIGHT

        self.matrix[y][x] ^= 1

        # was a pixel erased
        return not self.matrix[y][x]

    def clear(self) -> None:
        self.matrix = [[0 for x in range(SCREEN_WIDTH)] for y in range(SCREEN_HEIGHT)]
        pg.display.flip()

    def update(self) -> None:
        for y in range(SCREEN_HEIGHT):
            for x in range(SCREEN_WIDTH):
                color = WHITE if self.matrix[y][x] else BLACK
                pg.draw.rect(
                    self.screen,
                    color,
                    [
                        x * self.scaler,
                        y * self.scaler,
                        self.sprite_width,
                        self.sprite_height,
                    ],
                )
        pg.display.update()
