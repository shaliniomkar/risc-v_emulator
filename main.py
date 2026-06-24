from cpu import cpu
from loader import elf_loader
from debugger import gui

computer = cpu.CPU()
elf = elf_loader.ELFLoader(computer)

elf.load('test.elf')

window = gui.GUI(computer)
window.build_ui()