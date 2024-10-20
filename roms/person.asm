:alias px v1
:alias py v2

: main
  px := random 0b0011111
  py := random 0b0001111
  i  := person
  sprite px py 8

: person
  0x70 0x70 0x20 0x70 0xA8 0x20 0x50 0x50