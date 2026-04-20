from pathlib import Path

import pytest

from chip8.config import PC_INIT, REGISTER_COUNT
from chip8.cpu import CPU
from chip8.keypad import Keypad
from chip8.opcodes import opcodes
from chip8.ram import RAM
from chip8.screen import Screen


class DummyScreen(Screen):
    """Simple screen double for opcode tests."""

    def __init__(self) -> None:
        """Initialize the screen test double."""
        self.buffer = []
        self.clear_calls = 0
        self.flip_calls: list[tuple[int, int]] = []
        self.flip_results: list[bool] = []

    def clear(self) -> None:
        """Record each clear call."""
        # Keep track of CLS usage.
        self.clear_calls += 1

    def flip_pixel(self, x: int = 0, y: int = 0) -> bool:
        """Record pixel flips and return queued collision values."""
        # Provide deterministic draw collision behavior.
        self.flip_calls.append((x, y))
        if self.flip_results:
            return self.flip_results.pop(0)
        return False


class DummyKeypad(Keypad):
    """Simple keypad double for opcode tests."""

    def __init__(self) -> None:
        """Initialize the keypad test double."""
        self.pressed_keys = [0] * REGISTER_COUNT


@pytest.fixture
def cpu(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> CPU:
    """Create a CPU instance for opcode-level tests."""
    # Reset class-level CPU state before each instance is created.
    monkeypatch.setattr(CPU, "v", bytearray([0] * REGISTER_COUNT), raising=False)
    monkeypatch.setattr(CPU, "i", 0, raising=False)
    monkeypatch.setattr(CPU, "x", 0, raising=False)
    monkeypatch.setattr(CPU, "y", 0, raising=False)
    monkeypatch.setattr(CPU, "n", 0, raising=False)
    monkeypatch.setattr(CPU, "addr", 0, raising=False)
    monkeypatch.setattr(CPU, "kk", 0, raising=False)
    monkeypatch.setattr(CPU, "stack", [], raising=False)
    monkeypatch.setattr(CPU, "sound_timer", 0, raising=False)
    monkeypatch.setattr(CPU, "delay_timer", 0, raising=False)
    monkeypatch.setattr(CPU, "pc", PC_INIT, raising=False)

    rom_path = tmp_path / "empty.ch8"
    rom_path.write_bytes(b"")
    ram = RAM(str(rom_path))
    return CPU(ram, DummyScreen(), DummyKeypad())


def run_instruction(cpu: CPU, instruction: int) -> None:
    """Decode and execute one instruction at the current PC."""
    # Mirror one CPU step, including program-counter increment behavior.
    cpu.ram[cpu.pc] = (instruction >> 8) & 0xFF
    cpu.ram[cpu.pc + 1] = instruction & 0xFF
    cpu.decode()
    cpu.execute()
    assert cpu.opcode is not None
    if cpu.opcode.pc_inc:
        cpu.pc += cpu.opcode.length


def test_opcode_table_has_cpu_handlers() -> None:
    """Ensure every opcode points at an existing CPU method."""
    # Protect against opcode table drift.
    for opcode in opcodes.values():
        assert hasattr(CPU, opcode.call)


def test_00e0_cls(cpu: CPU) -> None:
    """Clear the display buffer."""
    # Verify CLS dispatches to screen clear.
    screen = cpu.screen
    assert isinstance(screen, DummyScreen)

    run_instruction(cpu, 0x00E0)

    assert screen.clear_calls == 1


def test_00ee_ret(cpu: CPU) -> None:
    """Return from subroutine."""
    # Verify RET restores PC from stack and moves to next instruction.
    cpu.stack.append(0x340)

    run_instruction(cpu, 0x00EE)

    assert cpu.pc == 0x342


def test_1nnn_jmp(cpu: CPU) -> None:
    """Jump to absolute address."""
    # Verify jump does not add an extra increment.
    run_instruction(cpu, 0x1234)
    assert cpu.pc == 0x234


def test_2nnn_call(cpu: CPU) -> None:
    """Call subroutine and push return address."""
    # Verify CALL stores current PC and jumps to nnn.
    run_instruction(cpu, 0x2456)
    assert cpu.stack == [PC_INIT]
    assert cpu.pc == 0x456


def test_3xkk_se_vx_kk(cpu: CPU) -> None:
    """Skip when Vx equals immediate."""
    # Verify skip distance is one extra instruction.
    cpu.v[0xA] = 0x11
    run_instruction(cpu, 0x3A11)
    assert cpu.pc == PC_INIT + 4


def test_4xkk_sne_vx_kk(cpu: CPU) -> None:
    """Skip when Vx does not equal immediate."""
    # Verify not-equal skip behavior.
    cpu.v[0xA] = 0x22
    run_instruction(cpu, 0x4A11)
    assert cpu.pc == PC_INIT + 4


def test_5xy0_se_vx_vy(cpu: CPU) -> None:
    """Skip when Vx equals Vy."""
    # Verify register-to-register equality skip.
    cpu.v[0xA] = 0x33
    cpu.v[0xB] = 0x33
    run_instruction(cpu, 0x5AB0)
    assert cpu.pc == PC_INIT + 4


def test_6xkk_ld_vx_kk(cpu: CPU) -> None:
    """Load immediate into register."""
    # Verify LD writes kk into Vx.
    run_instruction(cpu, 0x6A7F)
    assert cpu.v[0xA] == 0x7F


def test_7xkk_add_vx_kk(cpu: CPU) -> None:
    """Add immediate into register with wrapping."""
    # Verify 8-bit wraparound.
    cpu.v[0xA] = 250
    run_instruction(cpu, 0x7A0F)
    assert cpu.v[0xA] == 9


def test_8xy0_ld_vx_vy(cpu: CPU) -> None:
    """Copy Vy into Vx."""
    # Verify register assignment.
    cpu.v[0xB] = 0x77
    run_instruction(cpu, 0x8AB0)
    assert cpu.v[0xA] == 0x77


def test_8xy1_or_vx_vy(cpu: CPU) -> None:
    """Apply OR between Vx and Vy."""
    # Verify bitwise OR path.
    cpu.v[0xA] = 0b1010
    cpu.v[0xB] = 0b0110
    run_instruction(cpu, 0x8AB1)
    assert cpu.v[0xA] == 0b1110


def test_8xy2_and_vx_vy(cpu: CPU) -> None:
    """Apply AND between Vx and Vy."""
    # Verify bitwise AND path.
    cpu.v[0xA] = 0b1010
    cpu.v[0xB] = 0b0110
    run_instruction(cpu, 0x8AB2)
    assert cpu.v[0xA] == 0b0010


def test_8xy3_xor_vx_vy(cpu: CPU) -> None:
    """Apply XOR between Vx and Vy."""
    # Verify bitwise XOR path.
    cpu.v[0xA] = 0b1010
    cpu.v[0xB] = 0b0110
    run_instruction(cpu, 0x8AB3)
    assert cpu.v[0xA] == 0b1100


def test_8xy4_add_vx_vy(cpu: CPU) -> None:
    """Add Vy to Vx and set carry."""
    # Verify carry flag and wrapped result.
    cpu.v[0xA] = 250
    cpu.v[0xB] = 10
    run_instruction(cpu, 0x8AB4)
    assert cpu.v[0xA] == 4
    assert cpu.v[0xF] == 1


def test_8xy5_sub_vx_vy(cpu: CPU) -> None:
    """Subtract Vy from Vx and set not-borrow flag."""
    # Verify equal registers set VF to 1.
    cpu.v[0xA] = 7
    cpu.v[0xB] = 7
    run_instruction(cpu, 0x8AB5)
    assert cpu.v[0xA] == 0
    assert cpu.v[0xF] == 1


def test_8xy6_shr_vx(cpu: CPU) -> None:
    """Shift Vx right and move LSB into VF."""
    # Verify right-shift carry bit.
    cpu.v[0xA] = 0b1011
    run_instruction(cpu, 0x8AB6)
    assert cpu.v[0xA] == 0b0101
    assert cpu.v[0xF] == 1


def test_8xy7_subn_vx_vy(cpu: CPU) -> None:
    """Set Vx to Vy - Vx and set not-borrow flag."""
    # Verify equal registers keep VF set.
    cpu.v[0xA] = 5
    cpu.v[0xB] = 5
    run_instruction(cpu, 0x8AB7)
    assert cpu.v[0xA] == 0
    assert cpu.v[0xF] == 1


def test_8xye_shl_vx(cpu: CPU) -> None:
    """Shift Vx left and move MSB into VF."""
    # Verify MSB carry and 8-bit wrapping.
    cpu.v[0xA] = 0x80
    run_instruction(cpu, 0x8ABE)
    assert cpu.v[0xA] == 0
    assert cpu.v[0xF] == 1


def test_9xy0_sne_vx_vy(cpu: CPU) -> None:
    """Skip when Vx and Vy differ."""
    # Verify register inequality skip.
    cpu.v[0xA] = 1
    cpu.v[0xB] = 2
    run_instruction(cpu, 0x9AB0)
    assert cpu.pc == PC_INIT + 4


def test_annn_ld_i(cpu: CPU) -> None:
    """Load I with address immediate."""
    # Verify index register load.
    run_instruction(cpu, 0xA456)
    assert cpu.i == 0x456


def test_bnnn_jp_v0_addr(cpu: CPU) -> None:
    """Jump to nnn plus V0."""
    # Verify offset jump behavior.
    cpu.v[0] = 7
    run_instruction(cpu, 0xB123)
    assert cpu.pc == 0x12A


def test_cxkk_rnd(cpu: CPU, monkeypatch: pytest.MonkeyPatch) -> None:
    """Random masked byte into Vx."""
    # Verify random source is AND-masked by kk.
    monkeypatch.setattr("chip8.cpu.random.randint", lambda _a, _b: 0xAB)
    run_instruction(cpu, 0xCA0F)
    assert cpu.v[0xA] == 0x0B


def test_dxyn_draw(cpu: CPU) -> None:
    """Draw n-byte sprite and detect collision."""
    # Verify draw reads sprite bits and sets VF on collision.
    screen = cpu.screen
    assert isinstance(screen, DummyScreen)
    cpu.i = 0x300
    cpu.ram[cpu.i] = 0b1100_0000
    cpu.v[0xA] = 1
    cpu.v[0xB] = 2
    screen.flip_results = [False, True]

    run_instruction(cpu, 0xDAB1)

    assert screen.flip_calls == [(1, 2), (2, 2)]
    assert cpu.v[0xF] == 1


def test_ex9e_skp_vx(cpu: CPU) -> None:
    """Skip when key in Vx is pressed."""
    # Verify pressed-key skip path.
    keypad = cpu.keypad
    assert isinstance(keypad, DummyKeypad)
    cpu.v[0xA] = 5
    keypad.pressed_keys[5] = 1
    run_instruction(cpu, 0xEA9E)
    assert cpu.pc == PC_INIT + 4


def test_exa1_sknp_vx(cpu: CPU) -> None:
    """Skip when key in Vx is not pressed."""
    # Verify not-pressed key skip path.
    cpu.v[0xA] = 5
    run_instruction(cpu, 0xEAA1)
    assert cpu.pc == PC_INIT + 4


def test_fx07_ld_vx_dt(cpu: CPU) -> None:
    """Read delay timer into Vx."""
    # Verify timer read.
    cpu.delay_timer = 23
    run_instruction(cpu, 0xFA07)
    assert cpu.v[0xA] == 23


def test_fx0a_wait(cpu: CPU) -> None:
    """Wait for a key press and store key index in Vx."""
    # Verify no-key keeps PC steady and pressed key stores index.
    keypad = cpu.keypad
    assert isinstance(keypad, DummyKeypad)

    run_instruction(cpu, 0xFA0A)
    assert cpu.pc == PC_INIT

    keypad.pressed_keys[0xC] = 1
    run_instruction(cpu, 0xFA0A)
    assert cpu.v[0xA] == 0xC
    assert cpu.pc == PC_INIT + 2


def test_fx15_ld_dt_vx(cpu: CPU) -> None:
    """Write Vx into delay timer."""
    # Verify timer write.
    cpu.v[0xA] = 44
    run_instruction(cpu, 0xFA15)
    assert cpu.delay_timer == 44


def test_fx18_ld_st_vx(cpu: CPU) -> None:
    """Write Vx into sound timer."""
    # Verify timer write.
    cpu.v[0xA] = 55
    run_instruction(cpu, 0xFA18)
    assert cpu.sound_timer == 55


def test_fx1e_add_i_vx(cpu: CPU) -> None:
    """Add Vx to I."""
    # Verify index register addition.
    cpu.i = 0x300
    cpu.v[0xA] = 0x20
    run_instruction(cpu, 0xFA1E)
    assert cpu.i == 0x320


def test_fx29_ld_f_vx(cpu: CPU) -> None:
    """Load sprite address for hex digit in Vx."""
    # Verify 5-byte glyph indexing.
    cpu.v[0xA] = 0x9
    run_instruction(cpu, 0xFA29)
    assert cpu.i == 0x2D


def test_fx33_ld_b_vx(cpu: CPU) -> None:
    """Store BCD representation of Vx at I..I+2."""
    # Verify BCD conversion logic.
    cpu.i = 0x300
    cpu.v[0xA] = 231
    run_instruction(cpu, 0xFA33)
    assert cpu.ram[0x300] == 2
    assert cpu.ram[0x301] == 3
    assert cpu.ram[0x302] == 1


def test_fx55_ld_i_vx(cpu: CPU) -> None:
    """Store V0..Vx into memory starting at I."""
    # Verify register dump into RAM.
    cpu.i = 0x300
    cpu.v[0] = 9
    cpu.v[1] = 8
    cpu.v[2] = 7
    run_instruction(cpu, 0xF255)
    assert cpu.ram[0x300] == 9
    assert cpu.ram[0x301] == 8
    assert cpu.ram[0x302] == 7


def test_fx65_ld_vx_i(cpu: CPU) -> None:
    """Load V0..Vx from memory starting at I."""
    # Verify register load from RAM.
    cpu.i = 0x300
    cpu.ram[0x300] = 1
    cpu.ram[0x301] = 2
    cpu.ram[0x302] = 3
    run_instruction(cpu, 0xF265)
    assert cpu.v[0] == 1
    assert cpu.v[1] == 2
    assert cpu.v[2] == 3


def test_bitwise_vx_vy_rejects_invalid_symbol(cpu: CPU) -> None:
    """Reject unknown bitwise symbol."""
    # Guard against unsupported symbols.
    with pytest.raises(ValueError, match="Unsupported bitwise operator"):
        cpu.bitwise_vx_vy("%")
