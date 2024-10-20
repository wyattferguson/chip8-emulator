import pygame as pg
import pytest

from chip8.screen import Screen

screen_scale = 1
pg.init()
pg.display.set_caption(f"👾 Chip8 Emulator :: Running Screen Tests")
screen = Screen(pg, screen_scale)


def test_pixel_set():
    x, y = 2, 2
    screen.set_pixel(y, x, 1)
    assert screen.matrix[y][x] == 1


def test_clear():
    screen.set_pixel(5, 3, 1)
    screen.clear()
    for row in screen.matrix:
        for pixel in row:
            if pixel != 0:
                pytest.fail("Screen not clearing properly.")

    assert True
