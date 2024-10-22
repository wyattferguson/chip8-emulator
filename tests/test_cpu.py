import pygame as pg
import pytest

from chip8.cpu import CPU
from chip8.keyboard import Keyboard
from chip8.screen import Screen

screen_scale = 1
pg.init()
pg.display.set_caption(f"👾 Chip8 Emulator :: Running CPU Tests")
screen = Screen(screen_scale)
keyboard = Keyboard()


def test_registers():
    rom = "./roms/registers.ch8"

    cpu = CPU(rom, screen, keyboard)
    cpu.cycle()

    if hex(cpu.opcode) != "0xa007":
        pytest.fail(f"Opcode Read Wrong: {hex(cpu.opcode)} | 0xa007")

    if hex(cpu.X) != "0x0":
        pytest.fail(f"X Register Wrong: {hex(cpu.X)} | 0x0")

    if hex(cpu.Y) != "0x0":
        pytest.fail(f"Y Register Wrong: {hex(cpu.Y)} | 0x0")

    if hex(cpu.N) != "0x7":
        pytest.fail(f"N Register Wrong: {hex(cpu.N)} | 0x7")

    if cpu.V[1] != 9:
        pytest.fail("ADD Vx, KK Failed")

    assert True
