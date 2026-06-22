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
    
    def execute_r_type(self, fields):
        funct3 = fields['funct3']
        funct7 = fields['funct7']
        rs1 = fields['rs1']
        rs2 = fields['rs2']
        rd = fields['rd']

        val1 = self.regs.read(rs1)
        val2 = self.regs.read(rs2)

        dispatch_table = {
            (0x0, 0x00): "ADD",
            (0x0, 0x20): "SUB",
            (0x4, 0x00): "XOR",
            (0x6, 0x00): "OR",
            (0x7, 0x00): "AND",
            (0x1, 0x00): "SLL",
            (0x2, 0x00): "SLT",
            (0x3, 0x00): "SLTU",
            (0x5, 0x20): "SRA",
            (0x5, 0x00): "SRL"
        }

        def SRA(x, y):
            x_signed = self.sign_extend(x, 32)
            return (x_signed >> (y & 0x1F)) & 0xFFFFFFFF

        def SLT(x, y):
            x_signed = self.sign_extend(x, 32)
            y_signed = self.sign_extend(y, 32)

            if x_signed < y_signed:
                return 1
            else:
                return 0
            
        def SLTU(x, y):
            if x < y:
                return 1
            else:
                return 0

        operation_dict = {
            "ADD": lambda x, y: (x + y) & 0xFFFFFFFF,
            "SUB": lambda x, y: (x - y) & 0xFFFFFFFF,
            "XOR": lambda x, y: x ^ y,
            "OR": lambda x, y: x | y,
            "AND": lambda x, y: x & y,
            "SLL": lambda x, y: (x << (y & 0x1F)) & 0xFFFFFFFF,
            "SRL": lambda x, y: (x >> (y & 0x1F)) & 0xFFFFFFFF,
            "SRA": SRA,
            "SLT": SLT,
            "SLTU": SLTU
        }

        operation = dispatch_table.get((funct3, funct7))
        result = operation_dict[operation](val1, val2)

        self.regs.write(rd, result)
        self.pc += 4

    def execute_i_type(self, fields, instruction):
        funct3 = fields['funct3']
        bit_30 = (instruction >> 30) & 0x1
        rs1 = fields['rs1']
        immediate_value = self.imm_i(instruction)
        rd = fields['rd']

        val1 = self.regs.read(rs1)

        dispatch_table = {
            (0x0, 0): "ADDI",
            (0x4, 0): "XORI",
            (0x6, 0): "ORI",
            (0x7, 0): "ANDI",
            (0x2, 0): "SLTI",
            (0x3, 0): "SLTIU",
            (0x1, 0): "SLLI",
            (0x5, 0): "SRLI",
            (0x5, 1): "SRAI"
        }

        def SLTI(x):
            if self.sign_extend(x, 32) < immediate_value:
                return 1
            else:
                return 0
            
        def SLTIU(x):
            if x < (immediate_value & 0xFFFFFFFF):
                return 1
            else:
                return 0
            
        def SLLI(x):
            shift_amount = (instruction >> 20) & 0x1F
            return (x << shift_amount) & 0xFFFFFFFF
        
        def SRLI(x):
            shift_amount = (instruction >> 20) & 0x1F
            return (x >> shift_amount) & 0xFFFFFFFF
        
        def SRAI(x):
            extended = self.sign_extend(x, 32)
            shift_amount = (instruction >> 20) & 0x1F
            return (extended >> shift_amount) & 0xFFFFFFFF

        operation_dict = {
            "ADDI": lambda x: (x + immediate_value) & 0xFFFFFFFF,
            "XORI": lambda x: (x ^ immediate_value) & 0xFFFFFFFF,
            "ORI": lambda x: x | immediate_value,
            "ANDI": lambda x: x & immediate_value,
            "SLTI": SLTI,
            "SLTIU": SLTIU,
            "SLLI": SLLI,
            "SRLI": SRLI,
            "SRAI": SRAI
        }

        operation = dispatch_table.get((funct3, bit_30))
        result = operation_dict[operation](val1)

        self.regs.write(rd, result)
        self.pc += 4
        
    def execute_load(self, fields, instruction):
        funct3 = fields['funct3']
        rd = fields['rd']
        rs1 = fields['rs1']
        address = (fields['rs1'] + self.imm_i(instruction)) & 0xFFFFFFFF

        def LB(address):
            preprocessed = self.mem.read_address(address) 
            return self.sign_extend(preprocessed, 8)
        
        def LH(address):
            preprocessed = self.mem.read_halfword(address)
            return self.sign_extend(preprocessed, 16)
        
        def LW(address):
            return self.mem.read_word(address)
        
        def LBU(address):
            return self.mem.read_address(address) 

        def LHU(address):
            return self.mem.read_halfword(address) 
        
        dispatch_table = {
            0x0: "LB",
            0x1: "LH",
            0x2: "LW",
            0x4: "LBU",
            0x5: "LHU"
        }

        operation_dict = {
            "LB": LB,
            "LH": LH,
            "LW": LW,
            "LBU": LBU,
            "LHU": LHU
        }

        operation = dispatch_table.get(funct3)
        result = operation_dict[operation](address)

        self.regs.write(rd, result)
        self.pc += 4

    def execute_store(self, fields, instruction):
        funct3 = fields['funct3']
        rs1 = fields['rs1']
        val1 = self.regs.read(rs1)
        address = (val1 + self.imm_s(instruction)) & 0xFFFFFFFF
        value = self.regs.read(fields['rs2'])

        dispatch_table = {
            0x0: "SB",
            0x1: "SH",
            0x2: "SW"
        }

        def SB(address, value):
            self.mem.write_byte(address, value)

        def SH(address, value):
            self.mem.write_halfword(address, value)

        def SW(address, value):
            self.mem.write_word(address, value)

        operation_dict = {
            "SB": SB,
            "SH": SH,
            "SW": SW
        }

        operation = dispatch_table.get(funct3)
        operation_dict[operation](address, value)

        self.pc += 4

    def execute_branch(self, fields, instruction):
        old_pc = self.pc
        funct3 = fields['funct3']
        rs1 = fields['rs1']
        rs2 = fields['rs2']
        immediate_value = self.imm_b(instruction)

        val1 = self.regs.read(rs1)
        val2 = self.regs.read(rs2)

        dispatch_table = {
            0x0: "BEQ",
            0x1: "BNE",
            0x4: "BLT",
            0x5: "BGE",
            0x6: "BLTU",
            0x7: "BGEU" 
        }

        def BEQ(x, y):
            if x == y:
                return True
            else:
                return False
            
        def BNE(x, y):
            if x != y:
                return True
            else:
                return False
            
        def BLT(x, y):
            extend_1 = self.sign_extend(x, 32)
            extend_2 = self.sign_extend(y, 32)

            if extend_1 < extend_2:
                return True
            else:
                return False
            
        def BGE(x, y):
            extend_1 = self.sign_extend(x, 32)
            extend_2 = self.sign_extend(y, 32)

            if extend_1 >= extend_2:
                return True
            else:
                return False
            
        def BLTU(x, y):
            if x < y:
                return True
            else:
                return False
            
        def BGEU(x, y):
            if x >= y:
                return True
            else:
                return False
            
        operation_dict = {
            "BEQ": BEQ,
            "BNE": BNE,
            "BLT": BLT,
            "BGE": BGE,
            "BLTU": BLTU,
            "BGEU": BGEU
        }

        operation = dispatch_table.get(funct3)
        if operation_dict[operation](val1, val2):
            self.pc = old_pc + immediate_value
        else:
            self.pc = old_pc + 4



    def step(self):
        if self.pc >= len(self.mem):
            self.running = False
        fetched_instruction = self.mem.read_word(self.pc)
        fields = self.decode(fetched_instruction)
        opcode = fields['opcode']
    
computa = CPU()
fields = CPU.decode(computa, 0b00000001001001001000010000110011)
print(fields)

instruction = CPU.imm_j(computa, 0b00000000011001001000010000010011)
print(instruction)
