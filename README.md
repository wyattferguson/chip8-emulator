# Specifications

- Memory: CHIP-8 has direct access to up to 4 kilobytes of RAM
- Display: 64 x 32 pixels (or 128 x 64 for SUPER-CHIP) monochrome, ie. black or white
- A program counter, often called just “PC”, which points at the current instruction in memory
- One 16-bit index register called “I” which is used to point at locations in memory
- A stack for 16-bit addresses, which is used to call subroutines/functions and return from them
- An 8-bit delay timer which is decremented at a rate of 60 Hz (60 times per second) until it reaches 0
- An 8-bit sound timer which functions like the delay timer, but which also gives off a beeping sound as long as it’s not 0
- 16 8-bit (one byte) general-purpose variable registers numbered 0 through F hexadecimal, ie. 0 through 15 in decimal, called V0 through VF
- VF is also used as a flag register; many instructions will set it to either 1 or 0 based on some rule, for example using it as a carry flag

# Memory

The memory should be 4 kB (4 kilobytes, ie. 4096 bytes) large. CHIP-8’s index register and program counter can only address 12 bits (conveniently), which is 4096 addresses.

All the memory is RAM and should be considered to be writable. CHIP-8 games can, and do, modify themselves.

The first CHIP-8 interpreter (on the COSMAC VIP computer) was also located in RAM, from address 000 to 1FF. It would expect a CHIP-8 program to be loaded into memory after it, starting at address 200 (512 in decimal)

# Font

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

# Display

The display is 64 pixels wide and 32 pixels tall. Each pixel can be on or off. In other words, each pixel is a boolean value, or a bit.

Original interpreters updated the display at 60 Hz (60 FPS)

## Sprites

The drawing instruction DXYN in short, it is used to draw a “sprite” on the screen. Each sprite consists of 8-bit bytes, where each bit corresponds to a horizontal pixel; sprites are between 1 and 15 bytes tall. They’re drawn to the screen by treating all 0 bits as transparent, and all the 1 bits will “flip” the pixels in the locations of the screen that it’s drawn to. (You might recognize this as logical XOR.)

# Stack

CHIP-8 has a stack (a common “last in, first out” data structure where you can either “push” data to it or “pop” the last piece of data you pushed). You can represent it however you’d like; a stack if your programming language has it, or an array. CHIP-8 uses it to call and return from subroutines (“functions”) and nothing else, so you will be saving addresses there; 16-bit (or really only 12-bit) numbers.

# Timers

There are two separate timer registers: The delay timer and the sound timer. They both work the same way; they’re one byte in size, and as long as their value is above 0, they should be decremented by one 60 times per second (ie. at 60 Hz). This is independent of the speed of the fetch/decode/execute loop below.

The sound timer is special in that it should make the computer “beep” as long as it’s above 0.

# Keypad

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

# References

- Guide to making a CHIP-8 emulator ([https://tobiasvl.github.io/blog/write-a-chip-8-emulator/](https://tobiasvl.github.io/blog/write-a-chip-8-emulator/))
- CHIP-8 Wikipedia ([https://en.wikipedia.org/wiki/CHIP-8](https://en.wikipedia.org/wiki/CHIP-8))
- How to Create Your Very Own Chip-8 Emulator ([https://www.freecodecamp.org/news/creating-your-very-own-chip-8-emulator/](https://www.freecodecamp.org/news/creating-your-very-own-chip-8-emulator/))
- Bitwise Operators in Python ([https://realpython.com/python-bitwise-operators/#binary-number-representations](https://realpython.com/python-bitwise-operators/#binary-number-representations))
