from collections.abc import Callable
from pathlib import Path

import pytest

from chip8.config import FONT, MEMORY_SIZE, PC_INIT, REGISTERS_COUNT
from chip8.cpu import CPU
from chip8.keypad import Keypad
from chip8.screen import Screen


class DummyScreen(Screen):
    """Simple screen double for CPU tests."""

    def __init__(self) -> None:
        """Initialize the screen test double."""
        # Track clear and draw calls made by the CPU.
        self.clear_calls = 0
        self.flip_results: list[bool] = []
        self.flip_calls: list[tuple[int, int]] = []

    def clear(self) -> None:
        """Record each clear request."""
        # Record each screen clear operation.
        self.clear_calls += 1

    def flip_pixel(self, x: int = 0, y: int = 0) -> bool:
        """Record pixel flips and return queued collisions."""
        # Return queued collision results for draw tests.
        self.flip_calls.append((x, y))
        if self.flip_results:
            return self.flip_results.pop(0)
        return False


class DummyKeypad(Keypad):
    """Simple keypad double for CPU tests."""

    def __init__(self) -> None:
        """Initialize the keypad test double."""
        # Start with all CHIP-8 keys released.
        self.pressed_keys = [0] * REGISTERS_COUNT


@pytest.fixture
def cpu_factory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> Callable[..., tuple[CPU, DummyScreen, DummyKeypad]]:
    # Build a CPU with isolated shared state and a temporary ROM.
    def _make_cpu(rom_bytes: bytes = b"\x00\xe0") -> tuple[CPU, DummyScreen, DummyKeypad]:
        # Reset CPU class-level state before each instance is created.
        monkeypatch.setattr(CPU, "ram", bytearray([0] * MEMORY_SIZE))
        monkeypatch.setattr(CPU, "v", bytearray([0] * REGISTERS_COUNT))
        monkeypatch.setattr(CPU, "i", 0)
        monkeypatch.setattr(CPU, "x", 0)
        monkeypatch.setattr(CPU, "y", 0)
        monkeypatch.setattr(CPU, "n", 0)
        monkeypatch.setattr(CPU, "addr", 0)
        monkeypatch.setattr(CPU, "kk", 0)
        monkeypatch.setattr(CPU, "op_group", 0)
        monkeypatch.setattr(CPU, "cur_inst", None)
        monkeypatch.setattr(CPU, "stack", [])
        monkeypatch.setattr(CPU, "sound_timer", 0)
        monkeypatch.setattr(CPU, "delay_timer", 0)
        monkeypatch.setattr(CPU, "pc", PC_INIT)

        rom_path = tmp_path / "test.ch8"
        rom_path.write_bytes(rom_bytes)
        screen = DummyScreen()
        keypad = DummyKeypad()
        return CPU(str(rom_path), screen, keypad), screen, keypad

    return _make_cpu


def test_load_rom_populates_memory_and_font(
    cpu_factory: Callable[..., tuple[CPU, DummyScreen, DummyKeypad]],
) -> None:
    # Verify the ROM and built-in font are loaded into RAM.
    cpu, _, _ = cpu_factory(b"\x6a\x0f\x7a\x01")

    assert list(cpu.ram[: len(FONT)]) == FONT
    assert cpu.ram[PC_INIT : PC_INIT + 4] == bytearray(b"\x6a\x0f\x7a\x01")


def test_decode_extracts_opcode_fields(
    cpu_factory: Callable[..., tuple[CPU, DummyScreen, DummyKeypad]],
) -> None:
    # Decode an instruction into its operand fields.
    cpu, _, _ = cpu_factory(b"\xab\xcd")

    cpu.decode()

    assert cpu.opcode == 0xABCD
    assert cpu.x == 0xB
    assert cpu.y == 0xC
    assert cpu.n == 0xD
    assert cpu.addr == 0xBCD
    assert cpu.kk == 0xCD
    assert cpu.op_group == 0xA000


def test_execute_dispatches_current_opcode(
    cpu_factory: Callable[..., tuple[CPU, DummyScreen, DummyKeypad]],
) -> None:
    # Execute two instructions and verify register updates.
    cpu, _, _ = cpu_factory(b"\x6a\x0f\x7a\x01")

    cpu.decode()
    cpu.execute()
    cpu.pc += 2
    cpu.decode()
    cpu.execute()

    assert cpu.v[0xA] == 0x10


def test_cycle_runs_five_instructions_and_updates_timers(
    cpu_factory: Callable[..., tuple[CPU, DummyScreen, DummyKeypad]],
) -> None:
    # Run a cycle and verify timer and PC progression.
    cpu, screen, _ = cpu_factory(b"\x00\xe0" * 5)
    cpu.delay_timer = 2
    cpu.sound_timer = 1

    cpu.cycle()

    assert cpu.delay_timer == 1
    assert cpu.sound_timer == 0
    assert cpu.pc == PC_INIT + 10
    assert screen.clear_calls == 5


def test_draw_sets_collision_flag_when_pixel_erased(
    cpu_factory: Callable[..., tuple[CPU, DummyScreen, DummyKeypad]],
) -> None:
    # Draw a sprite row and propagate collision information into VF.
    cpu, screen, _ = cpu_factory()
    cpu.i = 0x300
    cpu.ram[cpu.i] = 0b1100_0000
    cpu.x = 1
    cpu.y = 2
    cpu.v[1] = 1
    cpu.v[2] = 2
    cpu.n = 1
    screen.flip_results = [False, True]

    cpu.draw()

    assert screen.flip_calls == [(1, 2), (2, 2)]
    assert cpu.v[0xF] == 1


def test_wait_rewinds_program_counter_until_key_press(
    cpu_factory: Callable[..., tuple[CPU, DummyScreen, DummyKeypad]],
) -> None:
    # Keep waiting when no key is pressed.
    cpu, _, keypad = cpu_factory()
    cpu.x = 3
    cpu.pc = PC_INIT + 4

    cpu.wait()

    assert cpu.pc == PC_INIT + 2
    keypad.pressed_keys[0xA] = True

    cpu.wait()

    assert cpu.pc == PC_INIT + 2
    assert cpu.v[3] == 0xA


def test_skp_vx_skips_when_pressed_state_matches(
    cpu_factory: Callable[..., tuple[CPU, DummyScreen, DummyKeypad]],
) -> None:
    # Skip the next instruction when the keypad state matches the opcode.
    cpu, _, keypad = cpu_factory()
    cpu.x = 4
    cpu.v[4] = 0x5
    keypad.pressed_keys[0x5] = 1

    cpu.skp_vx(True)

    assert cpu.pc == PC_INIT + 2
