import click

from ._config import DEFAULT_ROM, DEFAULT_SCALE
from .chip8 import Chip8


@click.command()
@click.option(
    "--rom",
    "-r",
    type=str,
    default=DEFAULT_ROM,
    is_flag=False,
    help="ROM file to run (.ch8 file).",
)
@click.option(
    "--debug",
    "-d",
    default=False,
    is_flag=True,
    help="Enable debug mode. Used only for development.",
)
@click.option(
    "--scale",
    "-s",
    default=DEFAULT_SCALE,
    is_flag=False,
    help="Scale multiplier for the screen size.",
)
def run(rom: str = DEFAULT_ROM, debug: bool = False, scale: int = DEFAULT_SCALE) -> None:
    """Run the Kanban application."""
    Chip8(rom, scale, debug).run()
