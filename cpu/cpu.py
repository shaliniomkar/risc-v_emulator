from cpu.registers import Register
from cpu.memory import Memory

class CPU:
    def __init__(self):
        self.regs = Register()
        self.mem = Memory()
        self.pc = 0
        self.running = True
    
    def decode(self, instruction):
        fields = {}
        fields['opcode'] = instruction & 0x7F
        fields['rd'] = instruction >> 7 & 0x1F
        fields['funct3'] = instruction >> 12 & 0x7
        fields['rs1'] = instruction >> 15 & 0x1F
        fields['rs2'] = instruction >> 20 & 0x1F
        fields['funct7'] = instruction >> 25 & 0x7F
        return fields
    
    @staticmethod
    def sign_extend(value, bits):
        mask = 1 << (bits - 1)
        return ((value & ((1 << bits) - 1)) ^ mask) - mask
    
    def imm_i(self, instruction):
        new_instruction = instruction >> 20
        extended_instruction = self.sign_extend(new_instruction, 12)
        return extended_instruction
    
    def imm_s(self, instruction):
        upper = instruction >> 25 & 0x7F
        lower = instruction >> 7 & 0x1F
        return self.sign_extend((upper << 5 | lower), 12)
    
    def imm_u(self, instruction):
        mask = 0xFFFFF000
        return instruction & mask
    
    def imm_b(self, instruction):
        # 12 11 10:5 4:1 "0"
        # 31 7 30:25 11:8 "0"
        bit_12 = instruction >> 31 & 0x1
        bit_11 = instruction >> 7 & 0x1
        bit_10_5 = instruction >> 25 & 0x3F
        bit_4_1 = instruction >> 8 & 0xF
        return self.sign_extend((bit_12 << 12 | bit_11 << 11 | bit_10_5 << 5 | bit_4_1 << 1 | 0), 12)
    
    def imm_j(self, instruction):
        # 20 10:1 11 19:12 "0"
        # 31 30:21 20 19:12 "0"
        bit_20 = instruction >> 31 & 0x1
        bit_10_1 = instruction >> 21 & 0x3FF
        bit_11 = instruction >> 20 & 0x1
        bit_19_12 = instruction >> 12 & 0xFF

        extended_instruction = self.sign_extend((bit_20 << 20 | bit_19_12 << 12 | bit_11 << 11 | bit_10_1 << 1 | 0), 21)
        return extended_instruction
    
    def execute_r_type(self, fields, instruction):
        dispatch_table = {
            "ADD": {"funct3": 0x0, "funct7": 0x00},
            "SUB": {"funct3": 0x0, "funct7": 0x20},
            "XOR": {"funct3": 0x4, "funct7": 0x00},
            "OR": {"funct3": 0x6, "funct7": 0x00},
            "AND": {"funct3": 0x7, "funct7": 0x00},
        }
    
    def step(self):
        if self.pc >= self.mem:
            self.running = False
        fetched_instruction = self.mem.read_word(self.pc)
        fields = self.decode(fetched_instruction)
        opcode = fields['opcode']
        
    
computa = CPU()
fields = CPU.decode(computa, 0b00000001001001001000010000110011)
print(fields)

instruction = CPU.imm_j(computa, 0b00000000011001001000010000010011)
print(instruction)
