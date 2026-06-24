from cpu import cpu
from loader import elf_loader
import tkinter as tk
from capstone import *

class GUI:
    md = Cs(CS_ARCH_RISCV, CS_MODE_RISCV32)
    def __init__(self, cpu):
        self.cpu = cpu
        self.root = tk.Tk()
        self.register_panel = tk.Frame(self.root, bg='lightblue')
        self.disassembly_panel = tk.Frame(self.root, bg='lightblue')
        self.memory_panel = tk.Frame(self.root, bg='lightblue')
        self.registers_list = tk.Listbox(self.register_panel)
        self.disassembly_list = tk.Listbox(self.disassembly_panel)
        self.memory_text = tk.Text(self.memory_panel)
        self.memory_address_entry = tk.Entry(self.memory_panel)
        self.loader = elf_loader.ELFLoader(cpu)
        self.memory_scrollbar = tk.Scrollbar(self.memory_panel)

    def build_ui(self):
        self.root.title("Risc-V Debugger")
        self.root.geometry("1200x700")

        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=0)
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=3)
        self.root.columnconfigure(2, weight=2)

        self.register_panel.grid(row=0, column=0, sticky="nsew")
        tk.Label(self.register_panel, text="Registers", bg="lightblue").pack(pady=20)

        self.registers_list.pack(padx=5, pady=5, fill="both", expand=True)
        self.refresh_registers()

        self.disassembly_panel.grid(row=0, column=1, sticky="nsew")
        tk.Label(self.disassembly_panel, text="Disassembly", bg="lightblue").pack(pady=20)

        self.disassembly_list.pack(padx=5, pady=5, fill="both", expand=True)
        self.refresh_disassembly()

        self.memory_panel.grid(row=0, column=2, sticky="nsew")
        tk.Label(self.memory_panel, text="Memory", bg="lightblue").pack(pady=20)

        tk.Label(self.memory_panel, text="Address:", bg="lightblue").pack()
        self.memory_address_entry.pack(padx=5, pady=5, fill="x")
        tk.Button(self.memory_panel, text="Go", command=self.refresh_memory).pack()

        self.memory_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.memory_text.pack(padx=5, pady=5, fill="both", expand=True)
        self.memory_address_entry.pack(padx=5, pady=5, fill="both", expand=True)
        self.memory_scrollbar.config(command=self.memory_text.yview)
        self.refresh_memory()


        button_bar = tk.Frame(self.root, bg="#D3D3D3", height=50)
        button_bar.grid(row=1, column=0, columnspan=3, sticky="ew")
        button_bar.pack_propagate(False) 

        step_button = tk.Button(button_bar, text="Step", command=self.on_step)
        step_button.pack(side=tk.LEFT, padx=10, pady=10)

        run_button = tk.Button(button_bar, text="Run", command=self.on_run)
        run_button.pack(side=tk.LEFT, padx=10, pady=10)

        reset_button = tk.Button(button_bar, text="Reset", command=self.on_reset)
        reset_button.pack(side=tk.LEFT, padx=10, pady=10)

        stop_button = tk.Button(button_bar, text="Stop", command=lambda: setattr(self.cpu, 'running', False))
        stop_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.root.mainloop()

    def refresh_registers(self):
        self.registers_list.delete(0, tk.END)
        for i in range(32):
            val = self.cpu.regs.read(i)
            name = self.cpu.regs.ABI_NAMES[i]
            line = f"x{i:02} ({name:>4}) = 0x{val:08X}"
            self.registers_list.insert(tk.END, line)

    def refresh_disassembly(self):
        self.disassembly_list.delete(0, tk.END)
        current_pc = self.cpu.pc if self.cpu.running else self.cpu.last_pc

        for i in range(-5, 6):
            address = current_pc + (i * 4)
            if address < 0 or address + 4 > len(self.cpu.mem._ba):
                continue
            word = self.cpu.mem.read_word(address)
            instruction_bytes = word.to_bytes(4, byteorder='little')

            for j in self.md.disasm(instruction_bytes, address):
                address_str = f"0x{j.address:08X}"
                bytes_str = "".join(f"{b:02X}" for b in j.bytes[:])
                formatted_line = f"{address_str}  {bytes_str}  {j.mnemonic} {j.op_str}"
                if address == current_pc:
                    formatted_line = f"-> {formatted_line}"
                    self.disassembly_list.insert(tk.END, formatted_line)
                    self.disassembly_list.itemconfig(tk.END, bg='yellow')
                else:
                    formatted_line = f"   {formatted_line}"
                    self.disassembly_list.insert(tk.END, formatted_line)

    def refresh_memory(self):
        self.memory_text.delete(1.0, tk.END)
        if self.memory_address_entry.get() != "":
            address = int(self.memory_address_entry.get(), 0)
        else:
            address = self.cpu.pc

        for row in range(32):
            line = bytes(self.cpu.mem._ba[address:address + 16])
            new_line = line.hex()
            row_string = new_text = " ".join(new_line[i:i+2] for i in range(0, len(new_line), 2))
            self.memory_text.insert(tk.END, f"Address {address:#010X}: {row_string}\n")
            address += 16

    def refresh(self):
        self.refresh_registers()
        self.refresh_disassembly()
        self.refresh_memory()

    def on_step(self):
        self.cpu.step()
        self.refresh()

    def on_run(self):
        self.cpu.run()
        self.refresh()

    def on_reset(self):
        self.cpu.reset()
        self.loader.load('test.elf')
        self.refresh()
