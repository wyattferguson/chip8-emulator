import pytest

from chip8.config import BLACK, PIXEL_HEIGHT, PIXEL_WIDTH, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE
from chip8.screen import Screen


@pytest.fixture
def patch_screen_pygame(monkeypatch: pytest.MonkeyPatch) -> dict[str, object]:
    # Replace pygame display and draw calls with recorders.
    calls: dict[str, object] = {
        "set_mode": None,
        "flip_calls": 0,
        "update_calls": 0,
        "rect_calls": [],
    }

    def _set_mode(size: tuple[int, int]) -> object:
        # Record the requested display size.
        calls["set_mode"] = size
        return object()

    def _flip() -> None:
        # Record display flip requests.
        calls["flip_calls"] = int(calls["flip_calls"]) + 1

    def _update() -> None:
        # Record display update requests.
        calls["update_calls"] = int(calls["update_calls"]) + 1

    def _rect(surface: object, color: tuple[int, int, int], rect: list[int]) -> None:
        # Record pixel draw requests.
        rect_calls = calls["rect_calls"]
        assert isinstance(rect_calls, list)
        rect_calls.append((surface, color, rect))

    monkeypatch.setattr("chip8.screen.pg.display.set_mode", _set_mode)
    monkeypatch.setattr("chip8.screen.pg.display.flip", _flip)
    monkeypatch.setattr("chip8.screen.pg.display.update", _update)
    monkeypatch.setattr("chip8.screen.pg.draw.rect", _rect)
    return calls


def test_screen_initializes_scaled_surface_and_blank_matrix(
    patch_screen_pygame: dict[str, object],
) -> None:
    # Build a screen with the requested scale factor.
    screen = Screen(3)

    assert patch_screen_pygame["set_mode"] == (SCREEN_WIDTH * 3, SCREEN_HEIGHT * 3)
    assert screen.sprite_width == PIXEL_WIDTH * 3
    assert screen.sprite_height == PIXEL_HEIGHT * 3
    assert len(screen.matrix) == SCREEN_HEIGHT
    assert len(screen.matrix[0]) == SCREEN_WIDTH
    assert all(pixel == 0 for row in screen.matrix for pixel in row)


def test_flip_pixel_wraps_and_reports_erasure(patch_screen_pygame: dict[str, object]) -> None:
    # Wrap coordinates around the display edges when toggling pixels.
    screen = Screen(1)

    assert screen.flip_pixel(SCREEN_WIDTH, SCREEN_HEIGHT) is False
    assert screen.matrix[0][0] == 1
    assert screen.flip_pixel(SCREEN_WIDTH, SCREEN_HEIGHT) is True
    assert screen.matrix[0][0] == 0


def test_clear_resets_entire_matrix_and_flips_display(
    patch_screen_pygame: dict[str, object],
) -> None:
    # Restore all pixels to the cleared state.
    screen = Screen(1)
    screen.matrix[0][0] = 1
    screen.matrix[5][5] = 1
    flip_calls = int(patch_screen_pygame["flip_calls"])

    screen.clear()

    assert all(pixel == 0 for row in screen.matrix for pixel in row)
    assert int(patch_screen_pygame["flip_calls"]) == flip_calls + 1


def test_update_draws_full_frame_and_refreshes_display(
    patch_screen_pygame: dict[str, object],
) -> None:
    # Draw every pixel in the current screen matrix.
    screen = Screen(2)
    screen.matrix[0][0] = 1

    screen.update()

    rect_calls = patch_screen_pygame["rect_calls"]
    assert isinstance(rect_calls, list)
    assert len(rect_calls) == SCREEN_WIDTH * SCREEN_HEIGHT
    assert rect_calls[0][1] == WHITE
    assert rect_calls[0][2] == [0, 0, PIXEL_WIDTH * 2, PIXEL_HEIGHT * 2]
    assert rect_calls[1][1] == BLACK
    assert patch_screen_pygame["update_calls"] == 1
