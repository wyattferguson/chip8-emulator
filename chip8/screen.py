import pygame as pg


class Screen(object):
    """Pygame Screen."""

    WIDTH = 64
    HEIGHT = 32
    PIXEL_WIDTH = 8
    PIXEL_HEIGHT = 8

    # Monochrome colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)

    matrix = []  # pixel representation of display

    def __init__(self, scaler: int = 10):
        self.sprite_width = self.PIXEL_WIDTH * scaler
        self.sprite_height = self.PIXEL_HEIGHT * scaler
        self.scaler = scaler

        self.screen = pg.display.set_mode((self.WIDTH * scaler, self.HEIGHT * scaler))
        self.clear()

    def set_pixel(self, x: int = 0, y: int = 0) -> bool:
        x %= self.WIDTH
        y %= self.HEIGHT

        self.matrix[y][x] ^= 1

        # was a pixel erased
        return not self.matrix[y][x]

    def clear(self):
        self.matrix = [[0 for x in range(self.WIDTH)] for y in range(self.HEIGHT)]
        pg.display.flip()

    def update(self):
        for y in range(self.HEIGHT):
            for x in range(self.WIDTH):
                color = self.WHITE if self.matrix[y][x] else self.BLACK
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
