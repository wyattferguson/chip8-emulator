###########################################
#
#  Tank
#
#  Classic Chip8 program translated from
#  VIPer Volume 1 Issue 1 (June 1978), pg 12-14
#  https://github.com/mattmikolay/viper/blob/master/volume1/issue1.pdf
#
#  Press 2/E/S/Q to move the tank.
#
###########################################

: tankup
  0x10 0x54 0x7c 0x6c 0x7c 0x7c
: tankdown
  0x44 0x7c 0x7c 0x6c 0x7c 0x54 0x10
: tankleft
  0x0 0xfc 0x78 0x6e 0x78 0xfc
: tankright
  0x0 0x3f 0x1e 0x76 0x1e 0x3f 0x0

: up    v2 += -1  i := tankup    ;
: down  v2 +=  1  i := tankdown  ;
: right v1 += -1  i := tankright ;
: left  v1 +=  1  i := tankleft  ;

: main
  v1 := 0x20
  v2 := 0x10
  i := tankup
  loop
    sprite v1 v2 7
    v0 := key
    sprite v1 v2 7
    if v0 == 2 then up
    if v0 == 4 then right
    if v0 == 6 then left
    if v0 == 8 then down
  again
