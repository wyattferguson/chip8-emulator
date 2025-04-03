![chip8pong](https://i.imgur.com/MdyWkCT.png)

# :robot: Chip-8 Emulator

This is my crack at creating a basic Chip-8 emulator as a learning exercise before moving onto more complicated systems. Its a great learning system since it only has 34 instructions and a simple memory layout. A few notes about my project:

- All 34 instructions are here +1 from the extended set.
- Screen has a flicker because of the way Im redrawing the pixels, but for this its good enough.
- Testing needs to be expanded for the cpu
- Some ROMS and assembly code for them has been included in the /roms/ folder.

The current version v0.2 of this emulator was just to clean up some old bugs and to add testing in preperation for a other larger emulator builds down the line.

## Development Setup

Installation is pretty straight forward, Im using [UV](https://docs.astral.sh/uv/) to manage everything.

To get it all running from scratch:

```
# spin up a virtual enviroment
uv venv

# activate virtual enviroment
.venv\Scripts\activate

# install all the cool dependancies
uv sync

# Run the default rom (tank.ch8)
task run

# You can pass another rom with the -r flag
task run -r ./roms/walk.ch8

# The screen scale can be adjusted with the -s flag (ie. -s 15 will scale is 15x the original resolution of 64x32)
task run -s 15

# lint source
task lint

# format source with ruff
task format

# run basic battery of pytests
task tests
```

## Chip8 Specifications

- Memory: CHIP-8 has direct access to up to 4 kilobytes of RAM
- Display: 64 x 32 pixels (or 128 x 64 for SUPER-CHIP) monochrome, ie. black or white
- A program counter, often called just “PC”, which points at the current instruction in memory
- One 16-bit index register called “I” which is used to point at locations in memory
- A stack for 16-bit addresses, which is used to call subroutines/functions and return from them
- An 8-bit delay timer which is decremented at a rate of 60 Hz (60 times per second) until it reaches 0
- An 8-bit sound timer which functions like the delay timer, but which also gives off a beeping sound as long as it’s not 0
- 16 8-bit (one byte) general-purpose variable registers numbered 0 through F hexadecimal, ie. 0 through 15 in decimal, called V0 through VF
- VF is also used as a flag register; many instructions will set it to either 1 or 0 based on some rule, for example using it as a carry flag

## Controls

The earliest computers that CHIP-8 were used with had hexadecimal keypads. These had 16 keys, labelled 0 through F, and were arranged in a 4x4 grid.

```
1 	2 	3 	C
4 	5 	6 	D
7 	8 	9 	E
A 	0 	B 	F
```

For CHIP-8 emulators that run on modern PCs, it’s customary to use the left side of the QWERTY keyboard for this:

```
1 	2 	3 	4
Q 	W 	E 	R
A 	S 	D 	F
Z 	X 	C 	V
```

## References

- Guide to making a CHIP-8 emulator ([https://tobiasvl.github.io/blog/write-a-chip-8-emulator/](https://tobiasvl.github.io/blog/write-a-chip-8-emulator/))
- Octo CHIP-8 Assember - ([https://johnearnest.github.io/Octo/](https://johnearnest.github.io/Octo/))
- CHIP-8 Wikipedia ([https://en.wikipedia.org/wiki/CHIP-8](https://en.wikipedia.org/wiki/CHIP-8))
- Bitwise Operators in Python ([https://realpython.com/python-bitwise-operators/#binary-number-representations](https://realpython.com/python-bitwise-operators/#binary-number-representations))
- Chip-8 Test Rom ([https://github.com/corax89/chip8-test-rom](https://github.com/corax89/chip8-test-rom))
- Chip-8 Variant Opcode Table ([https://chip8.gulrak.net/](https://chip8.gulrak.net/))

## License

[MIT license](https://github.com/wyattferguson/chip8-emulator/blob/master/LICENSE)

## Contact & Support

Created by [Wyatt Ferguson](https://github.com/wyattferguson)

For any questions or comments heres how you can reach me:

### :octocat: Follow me on [Github @wyattferguson](https://github.com/wyattferguson)

### :mailbox_with_mail: Email me at [wyattxdev@duck.com](wyattxdev@duck.com)

### :tropical_drink: Follow on [BlueSky @wyattf](https://wyattf.bsky.social)

If you find this useful and want to tip me a little coffee money:

### :coffee: [Buy Me A Coffee](https://www.buymeacoffee.com/wyattferguson)
