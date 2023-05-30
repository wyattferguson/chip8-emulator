
import pygame as pg

from config import (BLACK, DISPLAY_SCALER, FPS, SCREEN_HEIGHT, SCREEN_WIDTH,
                    WHITE)


class ChipScreen():

    def __init__(self):
        pg.init()
        pg.display.set_caption("Chip8 Emulator")

        self.screen_size = (SCREEN_WIDTH * DISPLAY_SCALER, SCREEN_HEIGHT * DISPLAY_SCALER)
        self.screen = pg.display.set_mode(self.screen_size)
        self.clock = pg.time.Clock()
        self.tick_speed = FPS
        self.running = True

    def update(self):
        # self.should_quit()
        pg.display.update()
        self.clock.tick(self.tick_speed)

    def clear_screen(self):
        self.screen.fill(BLACK)

    def flip(self,px,py):
        color = self.screen.get_at((px * DISPLAY_SCALER, py * DISPLAY_SCALER))

        if color == WHITE:
            pg.draw.rect(
                self.screen,
                BLACK,
                pg.Rect(px * DISPLAY_SCALER, py * DISPLAY_SCALER, DISPLAY_SCALER, DISPLAY_SCALER),
            )
            return True

        else:
            pg.draw.rect(
                self.screen,
                WHITE,
                pg.Rect(px * DISPLAY_SCALER, py * DISPLAY_SCALER, DISPLAY_SCALER, DISPLAY_SCALER),
            )
        return False

