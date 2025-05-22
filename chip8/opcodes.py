from dataclasses import dataclass


@dataclass
class OpCode:
    """Chip8 opcode with name and method to call."""

    label: str  # mnemonic name
    call: str  # CPU method name to call
    args: list[bool] | None = None  # give arguments to send to CPU method

    def __str__(self) -> str:
        return f"{self.label} - {self.call} - {self.args}"


# All standard Chip8 CPU Opcodes
opcodes: dict[int, OpCode] = {
    0x00E0: OpCode("CLS", "cls"),
    0x00EE: OpCode("RET", "ret"),
    0x1000: OpCode("JMP addr", "jmp"),
    0x2000: OpCode("CALL addr", "sub"),
    0x3000: OpCode("SE Vx, kk", "se_vx"),
    0x4000: OpCode("SNE Vx, kk", "sne_vx"),
    0x5000: OpCode("SE Vx, Vy", "se_vx_vy"),
    0x6000: OpCode("LD Vx, kk", "load_vx"),
    0x7000: OpCode("ADD Vx, kk", "add_vx_kk"),
    0x8000: OpCode("LD Vx, Vy", "set_vx_vy"),
    0x8001: OpCode("OR Vx, Vy", "or_vx_vy"),
    0x8002: OpCode("AND Vx, Vy", "and_vx_vy"),
    0x8003: OpCode("XOR Vx, Vy", "xor_vx_vy"),
    0x8004: OpCode("ADD Vx, Vy", "add_vx_vy"),
    0x8005: OpCode("SUB Vx, Vy", "sub_vx_vy"),
    0x8006: OpCode("SHR Vx {, Vy}", "shr_vx"),
    0x8007: OpCode("SUBN Vx, Vy", "subn_vx_vy"),
    0x800E: OpCode("SHL Vx {, Vy}", "shl_vx"),
    0x9000: OpCode("SNE Vx, Vy", "sne_vx_vy"),
    0xA000: OpCode("LD I, addr", "load_i"),
    0xB000: OpCode("JP V0, addr", "jmp_v0_addr"),
    0xC000: OpCode("RND Vx, kk", "rnd"),
    0xD000: OpCode("DRW Vx, Vy, n", "draw"),
    0xE09E: OpCode("SKP VX", "skp_vx", [True]),
    0xE0A1: OpCode("SKNP Vx", "skp_vx", [False]),
    0xF007: OpCode("LD Vx, DT", "load_vx_dt"),
    0xF00A: OpCode("WAIT", "wait"),
    0xF015: OpCode("LD DT, Vx", "load_dt_vx"),
    0xF018: OpCode("LD ST, Vx", "load_st_vx"),
    0xF01E: OpCode("ADD I, Vx", "add_i_vx"),
    0xF029: OpCode("LD F, Vx", "load_f_vx"),
    0xF033: OpCode("LD B, Vx", "load_bcd"),
    0xF055: OpCode("LD [I], Vx", "load_i_vx"),
    0xF065: OpCode("LD Vx, [I]", "load_vx_i"),
}
