![chip8pong](https://i.imgur.com/MdyWkCT.png)

# :robot: Chip-8 Emulator in Python

This is my Chip-8 emulator I built in Python. Created in 1977, CHIP-8 is the original fantasy console. Initially designed to ease game development for the COSMAC VIP kit computer. I built this as a learning project to get the basics of emulation. A few notes:

- All 34 instructions are here +1 from the extended set.
- Some ROMS for testing have been included in the `/roms/` folder.
- A full battery of tests to veryify opcode and hardware function.

## Setup + Run Emulator

Installation is pretty straight forward, Im using [UV](https://docs.astral.sh/uv/) to manage everything.

To get it all running from scratch:

```bash
# spin up a virtual enviroment
uv venv

# activate virtual enviroment
.venv\Scripts\activate

# install all the cool dependancies
uv sync

# Run the default rom (particle.ch8)
task run

# You can pass another rom with the -r flag
task run -r ./roms/walk.ch8

# The screen scale can be adjusted with the -s flag (ie. -s 15 will scale is 15x the original resolution of 64x32)
task run -s 15
```

## Development Tools

I've included a few shortcuts for linting, formating, and tests.

```bash
# lint source
task lint

# format source with ruff
task format

# run full battery of pytests
task tests
```

## Controls

For CHIP-8 emulators that run on modern PCs, it’s customary to use the left side of the QWERTY keyboard for this:

```bash
 CHIP-8:  1 2 3 C     Keyboard: 1 2 3 4
          4 5 6 D               Q W E R
          7 8 9 E               A S D F
          A 0 B F               Z X C V

                                Press ESC to Quit.
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
