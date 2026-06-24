from hexdump import hexdump

class Memory:
    def __init__(self, size=1024 * 1024):
        self._ba = bytearray(size)

    def read_address(self, address):
        if address + 1 > len(self._ba):
            raise ValueError(f"Memory access out of bounds at 0x{address:08X}")
        return int.from_bytes(self._ba[address:address + 1], byteorder='little')
    
    def read_halfword(self, address):
        if address + 2 > len(self._ba):
            raise ValueError(f"Memory access out of bounds at 0x{address:08X}")
        return int.from_bytes(self._ba[address:address + 2], byteorder='little')
    
    def read_word(self, address):
        if address + 4 > len(self._ba):
            raise ValueError(f"Memory access out of bounds at 0x{address:08X}")
        return int.from_bytes(self._ba[address:address + 4], byteorder='little')
    
    def write_byte(self, address, value):
        if address + 1 > len(self._ba):
            raise ValueError(f"Memory access out of bounds at 0x{address:08X}")
        self._ba[address] = value & 0xFF

    def write_halfword(self, address, value):
        if address + 2 > len(self._ba):
            raise ValueError(f"Memory access out of bounds at 0x{address:08X}")
        self._ba[address:address + 2] = (value & 0xFFFF).to_bytes(2, byteorder='little')

    def write_word(self, address, value):
        if address + 4 > len(self._ba):
            raise ValueError(f"Memory access out of bounds at 0x{address:08X}")
        self._ba[address:address + 4] = (value & 0xFFFFFFFF).to_bytes(4, byteorder='little')

    def load(self, address, data):
        if address + len(data) > len(self._ba):
            raise ValueError(f"Memory access out of bounds at 0x{address:08X}")
        self._ba[address:address + len(data)] = data

    def dump(self, address, length):
        if address + length > len(self._ba):
            raise ValueError(f"Memory access out of bounds at 0x{address:08X}")
        hexdump(self._ba[address:address + length])
        return self._ba[address:address + length]
