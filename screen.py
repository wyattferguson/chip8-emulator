import pygame as pg

from config import *


class ChipScreen():

    def __init__(self):
        pg.init()
        pg.display.set_caption(f"Chip8 Emulator- {ROM_FILE}")

        self.screen_size = ( SCREEN_WIDTH * DISPLAY_SCALER, SCREEN_HEIGHT * DISPLAY_SCALER)
        self.screen = pg.display.set_mode(self.screen_size)
        self.clock = pg.time.Clock()
        self.tick_speed = FPS
        self.running = True

    def clear(self):
        ''' Wipe current screen '''
        pass

    def update(self):
        # self.should_quit()
        pg.display.update()
        self.clock.tick(self.tick_speed)