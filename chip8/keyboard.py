import pygame as pg

from ._exceptions import KeypadError


class Keyboard:
    """16 Key hex keyboard ranging 1 to V."""

    def __init__(self, debug: bool = False) -> None:
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
        self.pressed_keys: list[int] = [0] * 16
        self.debug = debug

    def is_key_pressed(self, key_code: int) -> int:
        return self.pressed_keys[key_code]

    def update(self) -> None:
        for event in pg.event.get():
            # Press ESCAPE to quit emulator
            if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                pg.quit()
                exit()
            elif event.type == pg.KEYDOWN or event.type == pg.KEYUP:
                try:
                    key = self.key_map[event.key]
                    self.pressed_keys[key] = not self.pressed_keys[key]
                except Exception as e:
                    if self.debug:
                        raise KeypadError(f"Key press error: {event.key} :: {e}") from e
                    pass
