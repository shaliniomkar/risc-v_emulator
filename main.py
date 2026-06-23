from cpu import cpu
from loader import elf_loader

computer = cpu.CPU()
elf = elf_loader.ELFLoader(computer)

elf.load('test.elf')

print(f"sp = 0x{computer.regs.read(2):08X}")
print(f"pc = 0x{computer.pc:08X}")

computer.run()
computer.regs.dump()