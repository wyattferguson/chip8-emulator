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

## Memory Map

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

```
(0,0)	(63,0)
(0,31)	(63,31)
```

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

# Instructions

**0nnn - SYS addr**

Jump to a machine code routine at nnn.

This instruction is only used on the old computers on which Chip-8 was originally implemented. It is ignored by modern interpreters.

00E0 - CLS
Clear the display.

00EE - RET
Return from a subroutine.

The interpreter sets the program counter to the address at the top of the stack, then subtracts 1 from the stack pointer.

**1nnn - JP addr**
Jump to location nnn.
The interpreter sets the program counter to nnn.

2nnn - CALL addr
Call subroutine at nnn.

The interpreter increments the stack pointer, then puts the current PC on the top of the stack. The PC is then set to nnn.

3xkk - SE Vx, byte
Skip next instruction if Vx = kk.

The interpreter compares register Vx to kk, and if they are equal, increments the program counter by 2.

4xkk - SNE Vx, byte
Skip next instruction if Vx != kk.

The interpreter compares register Vx to kk, and if they are not equal, increments the program counter by 2.

5xy0 - SE Vx, Vy
Skip next instruction if Vx = Vy.

The interpreter compares register Vx to register Vy, and if they are equal, increments the program counter by 2.

**6xkk - LD Vx, byte**
Set Vx = kk.
The interpreter puts the value kk into register Vx.

7xkk - ADD Vx, byte
Set Vx = Vx + kk.

Adds the value kk to the value of register Vx, then stores the result in Vx.

8xy0 - LD Vx, Vy
Set Vx = Vy.

Stores the value of register Vy in register Vx.

8xy1 - OR Vx, Vy
Set Vx = Vx OR Vy.

Performs a bitwise OR on the values of Vx and Vy, then stores the result in Vx. A bitwise OR compares the corrseponding bits from two values, and if either bit is 1, then the same bit in the result is also 1. Otherwise, it is 0.

8xy2 - AND Vx, Vy
Set Vx = Vx AND Vy.

Performs a bitwise AND on the values of Vx and Vy, then stores the result in Vx. A bitwise AND compares the corrseponding bits from two values, and if both bits are 1, then the same bit in the result is also 1. Otherwise, it is 0.

8xy3 - XOR Vx, Vy
Set Vx = Vx XOR Vy.

Performs a bitwise exclusive OR on the values of Vx and Vy, then stores the result in Vx. An exclusive OR compares the corrseponding bits from two values, and if the bits are not both the same, then the corresponding bit in the result is set to 1. Otherwise, it is 0.

8xy4 - ADD Vx, Vy
Set Vx = Vx + Vy, set VF = carry.

The values of Vx and Vy are added together. If the result is greater than 8 bits (i.e., > 255,) VF is set to 1, otherwise 0. Only the lowest 8 bits of the result are kept, and stored in Vx.

8xy5 - SUB Vx, Vy
Set Vx = Vx - Vy, set VF = NOT borrow.

If Vx > Vy, then VF is set to 1, otherwise 0. Then Vy is subtracted from Vx, and the results stored in Vx.

8xy6 - SHR Vx {, Vy}
Set Vx = Vx SHR 1.

If the least-significant bit of Vx is 1, then VF is set to 1, otherwise 0. Then Vx is divided by 2.

8xy7 - SUBN Vx, Vy
Set Vx = Vy - Vx, set VF = NOT borrow.

If Vy > Vx, then VF is set to 1, otherwise 0. Then Vx is subtracted from Vy, and the results stored in Vx.

8xyE - SHL Vx {, Vy}
Set Vx = Vx SHL 1.

If the most-significant bit of Vx is 1, then VF is set to 1, otherwise to 0. Then Vx is multiplied by 2.

9xy0 - SNE Vx, Vy
Skip next instruction if Vx != Vy.

The values of Vx and Vy are compared, and if they are not equal, the program counter is increased by 2.

Annn - LD I, addr
Set I = nnn.

The value of register I is set to nnn.

Bnnn - JP V0, addr
Jump to location nnn + V0.

The program counter is set to nnn plus the value of V0.

Cxkk - RND Vx, byte
Set Vx = random byte AND kk.

The interpreter generates a random number from 0 to 255, which is then ANDed with the value kk. The results are stored in Vx. See instruction 8xy2 for more information on AND.

Dxyn - DRW Vx, Vy, nibble
Display n-byte sprite starting at memory location I at (Vx, Vy), set VF = collision.

The interpreter reads n bytes from memory, starting at the address stored in I. These bytes are then displayed as sprites on screen at coordinates (Vx, Vy). Sprites are XORed onto the existing screen. If this causes any pixels to be erased, VF is set to 1, otherwise it is set to 0. If the sprite is positioned so part of it is outside the coordinates of the display, it wraps around to the opposite side of the screen. See instruction 8xy3 for more information on XOR, and section 2.4, Display, for more information on the Chip-8 screen and sprites.

Ex9E - SKP Vx
Skip next instruction if key with the value of Vx is pressed.

Checks the keyboard, and if the key corresponding to the value of Vx is currently in the down position, PC is increased by 2.

ExA1 - SKNP Vx
Skip next instruction if key with the value of Vx is not pressed.

Checks the keyboard, and if the key corresponding to the value of Vx is currently in the up position, PC is increased by 2.

Fx07 - LD Vx, DT
Set Vx = delay timer value.

The value of DT is placed into Vx.

Fx0A - LD Vx, K
Wait for a key press, store the value of the key in Vx.

All execution stops until a key is pressed, then the value of that key is stored in Vx.

Fx15 - LD DT, Vx
Set delay timer = Vx.

DT is set equal to the value of Vx.

Fx18 - LD ST, Vx
Set sound timer = Vx.

ST is set equal to the value of Vx.

Fx1E - ADD I, Vx
Set I = I + Vx.

The values of I and Vx are added, and the results are stored in I.

Fx29 - LD F, Vx
Set I = location of sprite for digit Vx.

The value of I is set to the location for the hexadecimal sprite corresponding to the value of Vx. See section 2.4, Display, for more information on the Chip-8 hexadecimal font.

Fx33 - LD B, Vx
Store BCD representation of Vx in memory locations I, I+1, and I+2.

The interpreter takes the decimal value of Vx, and places the hundreds digit in memory at location in I, the tens digit at location I+1, and the ones digit at location I+2.

Fx55 - LD [I], Vx
Store registers V0 through Vx in memory starting at location I.

The interpreter copies the values of registers V0 through Vx into memory, starting at the address in I.

Fx65 - LD Vx, [I]
Read registers V0 through Vx from memory starting at location I.

The interpreter reads values from memory starting at location I into registers V0 through Vx.

# References

- Guide to making a CHIP-8 emulator ([https://tobiasvl.github.io/blog/write-a-chip-8-emulator/](https://tobiasvl.github.io/blog/write-a-chip-8-emulator/))
- CHIP-8 Wikipedia ([https://en.wikipedia.org/wiki/CHIP-8](https://en.wikipedia.org/wiki/CHIP-8))
- How to Create Your Very Own Chip-8 Emulator ([https://www.freecodecamp.org/news/creating-your-very-own-chip-8-emulator/](https://www.freecodecamp.org/news/creating-your-very-own-chip-8-emulator/))
- Bitwise Operators in Python ([https://realpython.com/python-bitwise-operators/#binary-number-representations](https://realpython.com/python-bitwise-operators/#binary-number-representations))
- Chip-8 Test Rom ([https://github.com/corax89/chip8-test-rom](https://github.com/corax89/chip8-test-rom))
