from elftools.elf.elffile import ELFFile
from cpu.cpu import CPU

class ELFLoader:
    def __init__(self, cpu):
        self.cpu = cpu

    def load(self, filename):
        with open(filename, 'rb') as f:
            elf = ELFFile(f)

            if elf.header['e_machine'] != "EM_RISCV":
                raise ValueError("File is not risc-v binary.")
            if elf.elfclass != 32:
                raise ValueError("Not 32 bit binary.")
            if not elf.little_endian:
                raise ValueError("Not little-endian encoded.")

            for segment in elf.iter_segments():
                if segment.header.p_type == 'PT_LOAD':
                    vaddr = segment.header.p_vaddr
                    files = segment.header.p_filesz
                    mems = segment.header.p_memsz
                    data = segment.data()

                    self.cpu.mem.load(vaddr, data)
                    if mems > files:
                        zero_count = mems - files
                        zero_start = vaddr + files
                        self.cpu.mem.load(zero_start, bytearray(zero_count))

            self.cpu.pc = elf.header['e_entry']
            
    

