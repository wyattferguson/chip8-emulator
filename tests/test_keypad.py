from types import SimpleNamespace

import pygame as pg
import pytest

from chip8.keypad import Keypad


def test_keypad_initializes_with_hex_layout() -> None:
    # Verify the keypad starts with the expected CHIP-8 layout.
    keypad = Keypad()

    assert len(keypad.key_map) == 16
    assert keypad.key_map[49] == 0x1
    assert keypad.key_map[120] == 0x0
    assert keypad.pressed_keys == [0] * 16


def test_is_key_pressed_returns_current_state() -> None:
    # Read the stored state for a mapped CHIP-8 key.
    keypad = Keypad()
    keypad.pressed_keys[0xA] = 1

    assert keypad.is_key_pressed(0xA) == 1


def test_update_toggles_pressed_key_state(monkeypatch: pytest.MonkeyPatch) -> None:
    # Process key down and key up events for a mapped key.
    keypad = Keypad()
    events = [
        SimpleNamespace(type=pg.KEYDOWN, key=49),
        SimpleNamespace(type=pg.KEYUP, key=49),
    ]
    monkeypatch.setattr(pg.event, "get", lambda: events)

    keypad.update()

    assert keypad.pressed_keys[0x1] == 0


def test_update_ignores_unmapped_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    # Leave keypad state unchanged for unrelated keys.
    keypad = Keypad()
    events = [SimpleNamespace(type=pg.KEYDOWN, key=pg.K_SPACE)]
    monkeypatch.setattr(pg.event, "get", lambda: events)

    keypad.update()

    assert keypad.pressed_keys == [0] * 16


def test_update_quits_on_escape(monkeypatch: pytest.MonkeyPatch) -> None:
    # Quit the emulator on escape.
    keypad = Keypad()
    escape_event = SimpleNamespace(type=pg.KEYDOWN, key=pg.K_ESCAPE)
    quit_called = False

    def _quit() -> None:
        # Record that pygame quit was requested.
        nonlocal quit_called
        quit_called = True

    monkeypatch.setattr(pg.event, "get", lambda: [escape_event])
    monkeypatch.setattr(pg, "quit", _quit)
    monkeypatch.setattr("chip8.keypad.sys.exit", lambda: (_ for _ in ()).throw(SystemExit()))

    with pytest.raises(SystemExit):
        keypad.update()

    assert quit_called is True
