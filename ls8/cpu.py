"""CPU functionality."""

import sys


HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
SP = 7


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.running = True
        self.reg[SP] = 0xf4
        self.dispatchtable = {}
        self.dispatchtable[HLT] = self.handle_HLT
        self.dispatchtable[LDI] = self.handle_LDI
        self.dispatchtable[PRN] = self.handle_PRN
        self.dispatchtable[MUL] = self.handle_MUL
        self.dispatchtable[PUSH] = self.handle_PUSH
        self.dispatchtable[POP] = self.handle_POP
        self.dispatchtable[CALL] = self.handle_CALL
        self.dispatchtable[RET] = self.handle_RET
        self.dispatchtable[ADD] = self.handle_ADD

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, address, value):
        self.ram[address] = value

    def handle_HLT(self):
        self.running = False

    def handle_LDI(self, a, b):
        self.reg[a] = b

    def handle_PRN(self, a):
        print(self.reg[a])

    def handle_MUL(self, a, b):
        self.alu('MUL', a, b)

    def handle_PUSH(self, a):
        self.reg[SP] -= 1
        self.ram_write(self.reg[SP], self.reg[a])

    def handle_POP(self, a):
        self.reg[a] = self.ram_read(self.reg[SP])
        self.reg[SP] += 1

    def handle_CALL(self, a):
        self.reg[SP] -= 1
        return_address = self.pc + 2
        self.ram[self.reg[SP]] = return_address
        given_register = self.reg[a]
        self.pc = given_register

    def handle_RET(self):
        return_address = self.ram[self.reg[SP]]
        self.reg[SP] += 1
        self.pc = return_address

    def handle_ADD(self, a, b):
        self.alu('ADD', a, b)

    def load(self):
        """Load a program into memory."""
        file_name = f'examples/{sys.argv[1]}.ls8'
        try:
            address = 0
            with open(file_name) as f:
                for line in f:
                    command = line.split('#')[0].strip()

                    if command == '':
                        continue
                    instruction = int(command, 2)
                    self.ram_write(address, instruction)
                    address += 1
        except FileNotFoundError:
            print(f'{sys.argv[0]} : {sys.argv[1]} file was not found')
            sys.exit()

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        while self.running:

            IR = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            instructions = (IR >> 6) + 1
            direct_set_instructions = ((IR >> 4) & 0b1) == 1

            if not direct_set_instructions:
                self.pc += instructions

            if IR in self.dispatchtable:
                if instructions == 1:
                    self.dispatchtable[IR]()
                elif instructions == 2:
                    self.dispatchtable[IR](operand_a)
                else:
                    self.dispatchtable[IR](operand_a, operand_b)
            else:
                print(f'Invalid instruction {bin(IR)} at {hex(self.pc)}')
