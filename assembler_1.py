import argparse
import re
import os

parser = argparse.ArgumentParser(prog="assembler_1.py", description="Assembler One")
parser.add_argument("file", metavar="FILE", type=argparse.FileType())
args = parser.parse_args()

INSTRUCTION_PATTERN = re.compile(r"([a-z]+)\s*([a-z#@0-9+]*)\s*(?:,\s*([a-z#@0-9+]*)\s*)?(?:,\s*([a-z#@0-9+]*)\s*)?", re.I)

labels = {}
instructions = []
offset = 0

class InputError(Exception):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


def remove_comment(line):
    return line.split(';', 1)[0]

def parse_operands(*operands):
    def parse_operand(operand):
        if operand == None:
            return ("NONE",)
        if operand == "@A+DPTR":
            return ("INDEXED", "DPTR")
        if operand == "@A+PC":
            return ("INDEXED", "PC")
        if operand == "A":
            return ("REGISTER_A",)
        if operand == "C":
            return ("BIT_C",)
        # Rn
        match = re.fullmatch("R([0-7])", operand)
        if match:
            return ("REGISTER_Rn", int(match[1]))
        # direct base 10
        match = re.fullmatch("(\d+)", operand)
        if match:
            return ("DIRECT", int(operand))
        # direct base 16
        match = re.fullmatch("(\d[a-z\d]+)h", operand, re.I)
        if match:
            return ("DIRECT", int(match[1], 16))
        # direct base 2
        match = re.fullmatch("(\d+)[by]", operand, re.I)
        if match:
            return ("DIRECT", int(match[1], 2))
        # immediate base 10
        match = re.fullmatch("#(\d+)", operand)
        if match:
            return ("IMMEDIATE", int(operand))
        # immediate base 16
        match = re.fullmatch("#(\d[a-z\d]+)h", operand, re.I)
        if match:
            return ("IMMEDIATE", int(match[1], 16))
        # immediate base 2
        match = re.fullmatch("#(\d+)[by]", operand, re.I)
        if match:
            return ("IMMEDIATE", int(match[1], 2))
        # register indirect
        match = re.fullmatch("@R([01])", operand)
        if match:
            return ("REGISTER_INDIRECT", int(match[1]))
        return ("LABEL", operand)
        # raise InputError(operand, "Invalid operand")
    return map(parse_operand, operands)

for line in args.file:
    line = remove_comment(line).strip()
    if line == "":
        continue
    print(line)
    # label = parse_label(line)
    # if label:
    #     continue
    match = INSTRUCTION_PATTERN.fullmatch(line)
    if match:
        opcode = match[1].upper()
        operands = tuple(parse_operands(match[2], match[3], match[4]))
        print(opcode)
        print(list(operands))
        if opcode == "MOV":
            if operands[0][0] == "REGISTER_A":
                if operands[1][0] == "DIRECT":
                    if operands[2][0] == "NONE":
                        instructions.append((offset, [0b11100101, operands[1][1]]))
                        continue
        elif opcode == "SETB":
            if operands[0][0] == "BIT_C":
                if operands[1][0] == "NONE" and operands[2][0] == "NONE":
                    instructions.append((offset, [0b11010011]))
                    continue
        elif opcode == "ADD":
            if operands[0][0] == "REGISTER_A":
                if operands[1][0] == "DIRECT":
                    if operands[2][0] == "NONE":
                        instructions.append((offset, [0b00100101, operands[1][1]]))
                        continue
        else:
            raise InputError(line, f"opcode not valid: {match[1]}")
        raise InputError(line, "Not implemented")
    else:
        raise InputError(line, "assembly not valid")

with open(os.path.basename(f"{os.path.splitext(args.file.name)[0]}-out.txt"), 'w') as file:
    for instruction in instructions:
        for _ in range(instruction[0]):
            file.write("00 ")
        for byte in instruction[1]:
            file.write(f"{byte:02X} ")


print(instructions)
print(labels)

args.file.close()