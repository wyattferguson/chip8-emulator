import pygame as pg


class Keyboard(object):
    """16 Key hex keyboard ranging 1 to V."""

    def __init__(self):
        self.key_map = {
            49: 0x1,  # 1
            50: 0x2,  # 2
            51: 0x3,  # 3
            52: 0xC,  # 4
            113: 0x4,  # Q
            119: 0x5,  # W
            101: 0x6,  # E
            114: 0xD,  # R
            97: 0x7,  # A
            115: 0x8,  # S
            100: 0x9,  # D
            102: 0xE,  # F
            122: 0xA,  # Z
            120: 0x0,  # X
            99: 0xB,  # C
            118: 0xF,  # V
        }
        self.pressed_keys = [False] * 16

    def is_key_pressed(self, key_code):
        return self.pressed_keys[key_code]

    def update(self):
        for event in pg.event.get():
            # Press ESCAPE to quit emulator
            if (
                event.type == pg.QUIT
                or event.type == pg.KEYDOWN
                and event.key == pg.K_ESCAPE
            ):
                pg.quit()
                exit()
            elif event.type == pg.KEYDOWN or event.type == pg.KEYUP:
                key = self.key_map[event.key]
                self.pressed_keys[key] = not self.pressed_keys[key]
