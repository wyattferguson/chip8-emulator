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

# Run the default rom (walk.ch8)
task run

# You can pass another rom with the -r flag
task run -r ./roms/tank.ch8

# The screen scale can be adjusted with the -s flag (ie. -s 15 will scale is 15x the original resolution of 64x32)
task run -s 15

# lint source
task lint

# format source with ruff
task format

# run basic battery of pytests
task tests
```

## Specifications

- Memory: CHIP-8 has direct access to up to 4 kilobytes of RAM
- Display: 64 x 32 pixels (or 128 x 64 for SUPER-CHIP) monochrome, ie. black or white
- A program counter, often called just “PC”, which points at the current instruction in memory
- One 16-bit index register called “I” which is used to point at locations in memory
- A stack for 16-bit addresses, which is used to call subroutines/functions and return from them
- An 8-bit delay timer which is decremented at a rate of 60 Hz (60 times per second) until it reaches 0
- An 8-bit sound timer which functions like the delay timer, but which also gives off a beeping sound as long as it’s not 0
- 16 8-bit (one byte) general-purpose variable registers numbered 0 through F hexadecimal, ie. 0 through 15 in decimal, called V0 through VF
- VF is also used as a flag register; many instructions will set it to either 1 or 0 based on some rule, for example using it as a carry flag

## Memory

The memory should be 4 kB (4 kilobytes, ie. 4096 bytes) large. CHIP-8’s index register and program counter can only address 12 bits (conveniently), which is 4096 addresses.

All the memory is RAM and should be considered to be writable. CHIP-8 games can, and do, modify themselves.

The first CHIP-8 interpreter (on the COSMAC VIP computer) was also located in RAM, from address 000 to 1FF. It would expect a CHIP-8 program to be loaded into memory after it, starting at address 200 (512 in decimal)

### Memory Map

    +---------------+= 0xFFF (4095) End of Chip-8 RAM
    |               |
    |               |
    |               |
    |               |
    |               |
    | 0x200 to 0xFFF|
    |     Chip-8    |
    | Program / Data|
    |     Space     |
    |               |
    |               |
    |               |
    +- - - - - - - -+= 0x600 (1536) ETI 660 Chip-8 programs
    |               |
    |               |
    |               |
    +---------------+= 0x200 (512) Chip-8 programs
    | 0x000 to 0x1FF|
    | Reserved for  |
    |  interpreter  |
    +---------------+= 0x000 (0) Start of Chip-8 RAM

## Font

The CHIP-8 emulator should have a built-in font, with sprite data representing the hexadecimal numbers from 0 through F. Each font character should be 4 pixels wide by 5 pixels tall. These font sprites are drawn just like regular sprites (see below).

```
0xF0, 0x90, 0x90, 0x90, 0xF0, // 0
0x20, 0x60, 0x20, 0x20, 0x70, // 1
0xF0, 0x10, 0xF0, 0x80, 0xF0, // 2
0xF0, 0x10, 0xF0, 0x10, 0xF0, // 3
0x90, 0x90, 0xF0, 0x10, 0x10, // 4
0xF0, 0x80, 0xF0, 0x10, 0xF0, // 5
0xF0, 0x80, 0xF0, 0x90, 0xF0, // 6
0xF0, 0x10, 0x20, 0x40, 0x40, // 7
0xF0, 0x90, 0xF0, 0x90, 0xF0, // 8
0xF0, 0x90, 0xF0, 0x10, 0xF0, // 9
0xF0, 0x90, 0xF0, 0x90, 0x90, // A
0xE0, 0x90, 0xE0, 0x90, 0xE0, // B
0xF0, 0x80, 0x80, 0x80, 0xF0, // C
0xE0, 0x90, 0x90, 0x90, 0xE0, // D
0xF0, 0x80, 0xF0, 0x80, 0xF0, // E
0xF0, 0x80, 0xF0, 0x80, 0x80  // F
```

## Display

The display is 64 pixels wide and 32 pixels tall. Each pixel can be on or off. In other words, each pixel is a boolean value, or a bit.

Original interpreters updated the display at 60 Hz (60 FPS)

```
(0,0)	(63,0)
(0,31)	(63,31)
```

## Sprites

The drawing instruction DXYN in short, it is used to draw a “sprite” on the screen. Each sprite consists of 8-bit bytes, where each bit corresponds to a horizontal pixel; sprites are between 1 and 15 bytes tall. They’re drawn to the screen by treating all 0 bits as transparent, and all the 1 bits will “flip” the pixels in the locations of the screen that it’s drawn to. (You might recognize this as logical XOR.)

## Stack

CHIP-8 has a stack (a common “last in, first out” data structure where you can either “push” data to it or “pop” the last piece of data you pushed). You can represent it however you’d like; a stack if your programming language has it, or an array. CHIP-8 uses it to call and return from subroutines (“functions”) and nothing else, so you will be saving addresses there; 16-bit (or really only 12-bit) numbers.

## Timers

There are two separate timer registers: The delay timer and the sound timer. They both work the same way; they’re one byte in size, and as long as their value is above 0, they should be decremented by one 60 times per second (ie. at 60 Hz). This is independent of the speed of the fetch/decode/execute loop below.

The sound timer is special in that it should make the computer “beep” as long as it’s above 0.

## Keypad

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

## Basic Instructions

    00E0 - CLS
    00EE - RET
    0nnn - SYS addr
    1nnn - JP addr
    2nnn - CALL addr
    3xkk - SE Vx, byte
    4xkk - SNE Vx, byte
    5xy0 - SE Vx, Vy
    6xkk - LD Vx, byte
    7xkk - ADD Vx, byte
    8xy0 - LD Vx, Vy
    8xy1 - OR Vx, Vy
    8xy2 - AND Vx, Vy
    8xy3 - XOR Vx, Vy
    8xy4 - ADD Vx, Vy
    8xy5 - SUB Vx, Vy
    8xy6 - SHR Vx {, Vy}
    8xy7 - SUBN Vx, Vy
    8xyE - SHL Vx {, Vy}
    9xy0 - SNE Vx, Vy
    Annn - LD I, addr
    Bnnn - JP V0, addr
    Cxkk - RND Vx, byte
    Dxyn - DRW Vx, Vy, nibble
    Ex9E - SKP Vx
    ExA1 - SKNP Vx
    Fx07 - LD Vx, DT
    Fx0A - LD Vx, K
    Fx15 - LD DT, Vx
    Fx18 - LD ST, Vx
    Fx1E - ADD I, Vx
    Fx29 - LD F, Vx
    Fx33 - LD B, Vx
    Fx55 - LD [I], Vx
    Fx65 - LD Vx, [I]

## References

- Guide to making a CHIP-8 emulator ([https://tobiasvl.github.io/blog/write-a-chip-8-emulator/](https://tobiasvl.github.io/blog/write-a-chip-8-emulator/))
- Octo CHIP-8 Assember - ([https://johnearnest.github.io/Octo/](https://johnearnest.github.io/Octo/))
- CHIP-8 Wikipedia ([https://en.wikipedia.org/wiki/CHIP-8](https://en.wikipedia.org/wiki/CHIP-8))
- Bitwise Operators in Python ([https://realpython.com/python-bitwise-operators/#binary-number-representations](https://realpython.com/python-bitwise-operators/#binary-number-representations))
- Chip-8 Test Rom ([https://github.com/corax89/chip8-test-rom](https://github.com/corax89/chip8-test-rom))
- Chip-8 Variant Opcode Table ([https://chip8.gulrak.net/](https://chip8.gulrak.net/))

- ## License

[MIT license](https://github.com/wyattferguson/chip8-emulator/blob/master/LICENSE)

## Contact & Support

Created by [Wyatt Ferguson](https://github.com/wyattferguson)

For any questions or comments heres how you can reach me:

### :octocat: Follow me on [Github @wyattferguson](https://github.com/wyattferguson)

### :mailbox_with_mail: Email me at [wyattxdev@duck.com](wyattxdev@duck.com)

### :tropical_drink: Follow on [BlueSky @wyattf](https://wyattf.bsky.social)

If you find this useful and want to tip me a little coffee money:

### :coffee: [Buy Me A Coffee](https://www.buymeacoffee.com/wyattferguson)
