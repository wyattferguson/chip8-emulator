import pygame as pg
import pytest

from chip8.cpu import CPU
from chip8.keypad import Keypad
from chip8.screen import Screen

screen_scale: int = 1
pg.init()
pg.display.set_caption("👾 Chip8 Emulator :: Running CPU Tests")
screen: Screen = Screen(screen_scale)
keypad: Keypad = Keypad()


def test_registers() -> None:
    rom: str = "./roms/registers.ch8"

    cpu = CPU(rom, screen, keypad)
    cpu.cycle()

    if hex(cpu.opcode) != "0xa007":
        pytest.fail(f"Opcode Read Wrong: {hex(cpu.opcode)} | 0xa007")

    if hex(cpu.x) != "0x0":
        pytest.fail(f"X Register Wrong: {hex(cpu.x)} | 0x0")

    if hex(cpu.y) != "0x0":
        pytest.fail(f"Y Register Wrong: {hex(cpu.y)} | 0x0")

    if hex(cpu.n) != "0x7":
        pytest.fail(f"N Register Wrong: {hex(cpu.n)} | 0x7")

    if cpu.v[1] != 9:
        pytest.fail("ADD Vx, KK Failed")

    assert True
