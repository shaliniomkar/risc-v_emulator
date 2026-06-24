class Register:

    ABI_NAMES = [
    "zero", "ra", "sp", "gp", "tp",
    "t0", "t1", "t2", "s0", "s1",
    "a0", "a1", "a2", "a3", "a4", "a5", "a6", "a7",
    "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10", "s11",
    "t3", "t4", "t5", "t6"
    ]

    def __init__(self):
        self._regs = [0] * 32

    def read(self, index):
        if not 0 <= index <= 31:
            raise IndexError(f"Register index {index} out of range.")
        return self._regs[index]
    
    def write(self, index, value):
        if index != 0:
            self._regs[index] = value & 0xFFFFFFFF
    
    def reset(self):
        self._regs = [0] * 32

    def dump(self):
        for i, val in enumerate(self._regs):
            print(f"x{i:02} = 0x{self.ABI_NAMES[i]:>4}  ({val})") 