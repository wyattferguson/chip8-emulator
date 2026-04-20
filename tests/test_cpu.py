from pathlib import Path

import pytest

from chip8.config import CPU_CYCLES_PER_TICK, FONT, PC_INIT, REGISTER_COUNT
from chip8.cpu import CPU
from chip8.keypad import Keypad
from chip8.ram import RAM
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
        self.pressed_keys = [0] * REGISTER_COUNT


@pytest.fixture
def cpu_factory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> CPU:
    """Build a CPU with reset class-level state and isolated doubles."""
    # Reset class-level mutable state for repeatable tests.
    monkeypatch.setattr(CPU, "v", bytearray([0] * REGISTER_COUNT))
    monkeypatch.setattr(CPU, "i", 0)
    monkeypatch.setattr(CPU, "x", 0)
    monkeypatch.setattr(CPU, "y", 0)
    monkeypatch.setattr(CPU, "n", 0)
    monkeypatch.setattr(CPU, "addr", 0)
    monkeypatch.setattr(CPU, "kk", 0)
    monkeypatch.setattr(CPU, "stack", [])
    monkeypatch.setattr(CPU, "sound_timer", 0)
    monkeypatch.setattr(CPU, "delay_timer", 0)
    monkeypatch.setattr(CPU, "pc", PC_INIT)

    rom_path = tmp_path / "cpu-smoke.ch8"
    rom_path.write_bytes(b"\x6a\x0f\x7a\x01" + (b"\x00\xe0" * 10))
    ram = RAM(str(rom_path))
    return CPU(ram, DummyScreen(), DummyKeypad())


def test_ram_starts_with_font_and_rom_bytes(cpu_factory: CPU) -> None:
    """RAM should contain font bytes and ROM payload."""
    # Validate RAM composition from RAM loader behavior.
    cpu = cpu_factory
    assert cpu.ram[: len(FONT)] == FONT
    assert cpu.ram[PC_INIT : PC_INIT + 4] == [0x6A, 0x0F, 0x7A, 0x01]


def test_decode_and_execute_progress_instruction(cpu_factory: CPU) -> None:
    """Decode and execute should update register state."""
    # Execute two instructions and check arithmetic result.
    cpu = cpu_factory
    cpu.decode()
    cpu.execute()
    cpu.pc += cpu.opcode.length
    cpu.decode()
    cpu.execute()
    assert cpu.v[0xA] == 0x10


def test_cycle_runs_configured_instructions_and_timers(cpu_factory: CPU) -> None:
    """Cycle should execute configured opcodes and decrement timers once."""
    # Verify cycle scheduling and timer ticks.
    cpu = cpu_factory
    screen = cpu.screen
    assert isinstance(screen, DummyScreen)
    cpu.delay_timer = 2
    cpu.sound_timer = 1

    cpu.cycle()

    assert cpu.delay_timer == 1
    assert cpu.sound_timer == 0
    assert cpu.pc == PC_INIT + (CPU_CYCLES_PER_TICK * 2)
    assert screen.clear_calls == 10
