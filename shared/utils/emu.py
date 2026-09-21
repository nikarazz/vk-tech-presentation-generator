from shared.constants import EMU_PER_INCH, EMU_PER_PT

def emu_to_inch(emu: int) -> float:
    return emu / EMU_PER_INCH

def emu_to_pt(emu: int) -> float:
    return emu / EMU_PER_PT

def inch_to_emu(inch: float) -> int:
    return int(inch * EMU_PER_INCH)

def pt_to_emu(pt: float) -> int:
    return int(pt * EMU_PER_PT)