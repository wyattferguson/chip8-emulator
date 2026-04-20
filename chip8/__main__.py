import click

from chip8.chip8 import Chip8
from chip8.config import DEFAULT_ROM, DEFAULT_SCALE


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
def run(rom: str, debug: bool, scale: int) -> None:
    """Run the CHIP-8 emulator."""
    Chip8(rom, scale, debug).run()
