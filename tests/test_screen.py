import pygame as pg
import pytest

from chip8.screen import Screen

screen_scale: int = 1
pg.init()
pg.display.set_caption("👾 Chip8 Emulator :: Running Screen Tests")
screen: Screen = Screen(screen_scale)


def test_pixel_set() -> None:
    """Turn on a pixel and check its set properly in the screen matrix."""
    x: int = 2
    y: int = 2
    screen.flip_pixel(y, x)
    assert screen.matrix[y][x] == 1


def test_clear() -> None:
    """Flip a few pixels and then test clearing the screen."""
    screen.flip_pixel(5, 3)
    screen.flip_pixel(2, 2)
    screen.clear()
    for row in screen.matrix:
        for pixel in row:
            if pixel != 0:
                pytest.fail("Screen not clearing properly.")

    assert True
