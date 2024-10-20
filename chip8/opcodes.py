from dataclasses import dataclass


@dataclass(frozen=True)
class OpCode:
    label: str  # mnemonic name
    call: str  # CPU method name to call
    args: list = None  # give arguments to send to CPU method

    def __str__(self) -> str:
        return f"{self.label} - {self.call} - {self.args}"


OPCODES = {
    0x00E0: OpCode("CLS", "CLS"),
    0x00EE: OpCode("RET", "RET"),
    0x1000: OpCode("JMP addr", "JMP"),
    0x2000: OpCode("CALL addr", "SUB"),
    0x3000: OpCode("SE Vx, kk", "SE_VX"),
    0x4000: OpCode("SNE Vx, kk", "SNE_VX"),
    0x5000: OpCode("SE Vx, Vy", "SE_VX_VY"),
    0x6000: OpCode("LD Vx, kk", "LOAD_VX"),
    0x7000: OpCode("ADD Vx, kk", "ADD_VX_KK"),
    0x8000: OpCode("LD Vx, Vy", "SET_VX_VY"),
    0x8001: OpCode("OR Vx, Vy", "OR_VX_VY"),
    0x8002: OpCode("AND Vx, Vy", "AND_VX_VY"),
    0x8003: OpCode("XOR Vx, Vy", "XOR_VX_VY"),
    0x8004: OpCode("ADD Vx, Vy", "ADD_VX_VY"),
    0x8005: OpCode("SUB Vx, Vy", "SUB_VX_VY"),
    0x8006: OpCode("SHR Vx {, Vy}", "SHR_VX"),
    0x8007: OpCode("SUBN Vx, Vy", "SUBN_VX_VY"),
    0x800E: OpCode("SHL Vx {, Vy}", "SHL_VX"),
    0x9000: OpCode("SNE Vx, Vy", "SNE_VX_VY"),
    0xA000: OpCode("LD I, addr", "LOAD_I"),
    0xB000: OpCode("JP V0, addr", "JMP_V0_ADDR"),
    0xC000: OpCode("RND Vx, kk", "RND"),
    0xD000: OpCode("DRW Vx, Vy, n", "DRAW"),
    0xE09E: OpCode("SKP VX", "SKP_VX", [True]),
    0xE0A1: OpCode("SKNP Vx", "SKP_VX", [False]),
    0xF007: OpCode("LD Vx, DT", "LOAD_VX_DT"),
    0xF00A: OpCode("WAIT", "WAIT"),
    0xF015: OpCode("LD DT, Vx", "LOAD_DT_VX"),
    0xF018: OpCode("LD ST, Vx", "LOAD_ST_VX"),
    0xF01E: OpCode("ADD I, Vx", "ADD_I_VX"),
    0xF029: OpCode("LD F, Vx", "LOAD_F_VX"),
    0xF033: OpCode("LD B, Vx", "LOAD_BCD"),
    0xF055: OpCode("LD [I], Vx", "LOAD_I_VX"),
    0xF065: OpCode("LD Vx, [I]", "LOAD_VX_I"),
}
