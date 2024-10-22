import pygame as pg
import pytest

from chip8.screen import Screen

screen_scale = 1
pg.init()
pg.display.set_caption(f"👾 Chip8 Emulator :: Running Screen Tests")
screen = Screen(screen_scale)


def test_pixel_set():
    """Turn on a pixel and check its set properly in the screen matrix"""
    x, y = 2, 2
    screen.set_pixel(y, x)
    assert screen.matrix[y][x] == 1


def test_clear():
    """Flip a few pixels and then test clearing the screen"""
    screen.set_pixel(5, 3)
    screen.set_pixel(2, 2)
    screen.clear()
    for row in screen.matrix:
        for pixel in row:
            if pixel != 0:
                pytest.fail("Screen not clearing properly.")

    assert True
