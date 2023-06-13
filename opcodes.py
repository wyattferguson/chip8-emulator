from dataclasses import dataclass


@dataclass(frozen=True)
class OpCode:
    label: str   # mnemonic name
    call: str    # CPU method name to call
    args: list = None   # give arguments to send to CPU method
    flags: tuple = None

    def __str__(self) -> str:
        return f"{self.label} - {self.args}"


OPCODES = {
    0x0000: OpCode("EXTRAS"),
    0x1000: "JMP",
    0x2000: "SUB",
    0x3000: "SE_VX",
    0x4000: "SNE_VX",
    0x5000: "SE_VX_VY",
    0x6000: "LOAD_VX",
    0x7000: "ADD_VX_KK",
    0x8000: "LOGICAL",
    0x9000: "SNE_VX_VY",
    0xa000: "LOAD_I",
    0xb000: "JMP_V0_ADDR",
    0xc000: "RND",
    0xd000: "DRAW",
    0xe000: "EXTRAS",
    0xf000: "EXTRAS"
}

# 0xX000 primary instructions set
code_lookup = {
    0x0000: "EXTRAS",
    0x1000: "JMP",
    0x2000: "SUB",
    0x3000: "SE_VX",
    0x4000: "SNE_VX",
    0x5000: "SE_VX_VY",
    0x6000: "LOAD_VX",
    0x7000: "ADD_VX_KK",
    0x8000: "LOGICAL",
    0x9000: "SNE_VX_VY",
    0xa000: "LOAD_I",
    0xb000: "JMP_V0_ADDR",
    0xc000: "RND",
    0xd000: "DRAW",
    0xe000: "EXTRAS",
    0xf000: "EXTRAS"
}

# 0x800X specific instructions
logical_lookup = {
    0x0: "SET_VX_VY",
    0x1: "OR_VX_VY",
    0x2: "AND_VX_VY",
    0x3: "XOR_VX_VY",
    0x4: "ADD_VX_VY",
    0x5: "SUB_VX_VY",
    0x6: "SHR_VX",
    0x7: "SUBN_VX_VY",
    0xe: "SHL_VX"
}

# 0x0/0xe/0xf & Super Chip-48 instructions
extra_lookup = {
    0x0007: "LOAD_VX_DT",
    0x000e: "SKP_VX",
    0x000a: "WAIT",
    0x00a1: "SKNP_VX",
    0x0015: "LOAD_DT_VX",
    0x0018: "LOAD_ST_VX",
    0x001e: "ADD_I_VX",
    0x0029: "LOAD_F_VX",
    0x0030: "LOAD_I_VX_EXT",
    0x0033: "LOAD_BCD",
    0x0055: "LOAD_I_VX",
    0x0065: "LOAD_VX_I",
    0x009e: "SKP_VX",
    0x00e0: OpCode("CLS","CLS"),
    0x00ee: "RET"
}
