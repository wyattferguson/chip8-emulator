
import pygame as pg

from config import (BLACK, DISPLAY_SCALER, FPS, SCREEN_HEIGHT, SCREEN_WIDTH,
                    WHITE)


class ChipScreen():

    def __init__(self):
        pg.init()
        pg.display.set_caption("Chip8 Emulator")

        self.keys = "1234qwerasdfzxcv"
        self.key_codes = [pg.key.key_code(key) for key in self.keys]
        self.pressed_keys = [False] * 16
        self.screen_size = (SCREEN_WIDTH * DISPLAY_SCALER, SCREEN_HEIGHT * DISPLAY_SCALER)
        self.screen = pg.display.set_mode(self.screen_size)
        self.clock = pg.time.Clock()
        self.tick_speed = FPS

    def update(self):
        self.keyboard()
        pg.display.update()
        self.clock.tick(self.tick_speed)

    def clear_screen(self):
        """black out entire screen"""
        self.screen.fill(BLACK)

    def flip(self, px, py):
        """Flip color of given pixel BLACK/WHITE"""
        scaled_pixel = (px * DISPLAY_SCALER, py * DISPLAY_SCALER)
        color = self.screen.get_at(scaled_pixel)
        swapped_color = BLACK if color == WHITE else WHITE

        pg.draw.rect(
            self.screen,
            swapped_color,
            pg.Rect(*scaled_pixel, DISPLAY_SCALER, DISPLAY_SCALER),
        )

        return color == WHITE

    def keyboard(self):
        """handle keypresses and quit events"""
        for event in pg.event.get():

            if event.type == pg.KEYDOWN or event.type == pg.KEYUP:
                if event.key in self.key_codes:
                    key_idx = self.key_codes.index(event.key)
                    self.pressed_keys[key_idx] = not self.pressed_keys[key_idx]

            if event.type == pg.QUIT:
                pg.quit()
                exit()
