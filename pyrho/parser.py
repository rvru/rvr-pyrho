"""
Parser Class for Disassembly

The ParseRules class determines the start/end of functions as well as extracts
data from parsed lines.

Author: Jennifer Hellar (jenniferhellar@proton.me)

"""


import re
from constants import *
import excel


class ParseRules:
    def __init__(self, compiler):
        self.compiler = compiler

    def is_func_start(self, line):
        """ Returns TRUE if input line is the initialization of a function. """
        if (self.compiler == 'rviar'):
            res = re.search(r'^\s\s\?*`*[a-zA-Z_]\w+`*:', line)
        else:
            res = re.search(r'^\w+\s<.+>:', line)
        return (res is not None)

    # def is_func_end(self, line):
    #     """
    #     Returns TRUE if input line is the end of a function during parsing.
    #     """
    #     # Check if new function or empty line
    #     # Check if $d (data) or $t (table) section (IAR only)
    #     res = self.is_func_start(line) \
    #         or line.strip() == '' \
    #         or ((re.search(r'^\s\s`*[$a-zA-Z_][d.]*\w+`*:', line) is not None)
    #             and self.compiler == 'IAR')
    #     return res

    # def is_end(self, line):
    #     """
    #     Returns TRUE if input line is the end of the last function to parse.
    #     """
    #     res = (line.strip() == '...')
    #     return res

    def is_skippable(self, line):
        """
        Returns TRUE if input line should not be parsed (data or empty).
        """
        res = (line.find('.word') != -1) \
            or (line.find('.short') != -1) \
            or (line.strip() == '') \
            or (line.find('.text') != -1) \
            or (line.find('.iar') != -1) \
            or (line.find('Region') != -1) \
            or (line.find('...') != -1) \
            or (line.find('file format') != -1) \
            or (line.find('Disassembly') != -1)
        return res

    def get_func_data(self, line):
        """
        Parses a line of text which contains a function initialization.

        Example line: "000103c2 <sglib___rbtree_fix_right_deletion_discrepancy>:"

        Returns a tuple of:
            - full name (sglib___rbtree_fix_right_deletion_discrepancy)
            - short name (fix_right_deletion_discrepancy) suitable for
                naming an Excel worksheet
        """
        lin_split = re.split(' ', line)
        lin_split[:] = [str(x).strip() for x in lin_split if str(x) != '']

        full_name = ''
        name = None
        # Choose functions to parse and generate wksheet names (<30 char)
        if (self.compiler[:2] == 'rv'):
            # Function name
            full_name = lin_split[1]
            # Exclude extra characters <>:
            full_name = full_name[1:-2]
            if len(full_name) > 30:
                name = full_name[-30:]
            else:
                name = full_name
            # These are the same for any benchmark
            if (save_restore_en):
                if (full_name[0:12] == '__riscv_save'):
                    name = '__riscv_save'
                elif (full_name[0:15] == '__riscv_restore'):
                    name = '__riscv_restore'
            excel.wksheet_names[full_name] = name
        elif (self.compiler[:3] == 'arm'):
            # Function name
            full_name = lin_split[1]
            # Exclude extra characters <>:
            full_name = full_name[1:-2]
            if full_name in excel.wksheet_names.keys():
                name = excel.wksheet_names[full_name]
        return (full_name, name)

    def scan_rvgcc_instruction(self, line):
        """
        Parses a line of text which contains an RVGCC instruction.

        Example: "   10084:    8e81a783            lw  a5,-1816(gp) # 127f4"

        Returns a tuple of:
            - Memory address of the instruction (addr = 10084)
            - Hex machine code of the instruction (instr = 8e81a783)
            - Size of the instruction (bytes = 4)
            - Opcode (lw, beqz, etc.) of the instruction (opcode = lw)
            - Registers and other arguments (args = [a5, -1816(gp)])
            - Disassembly comments (remainder = '# 127f4')
        """
        # Split line by spaces, tabs, and commas (and strip any whitespace)
        lin_split = re.split(r'[ \t,]', line)
        lin_split[:] = [str(x).strip() for x in lin_split if str(x) != '']
        # Memory location of instruction
        addr = lin_split[0][:-1]
        # Machine code (hex) gives instruction size
        instr = lin_split[1]
        bytes = len(instr)/2
        # Opcode (lw, beqz, etc.)
        opcode = lin_split[2]
        # Args and comments more complicated since not always present/uniform
        args = []
        remainder = ''
        # ret has no additional inputs
        if (opcode != 'ret'):
            arg_lst = lin_split[3:]
            num_args = len(arg_lst)
            for i in range(num_args):
                arg = arg_lst[i]
                # These two cases indicate the start of comments
                if (arg[0] == '<') or (arg == '#'):
                    # if comments found, args is everything up to that
                    args = arg_lst[:i]
                    while i < num_args:  # remainder is everything after
                        remainder = remainder + ' ' + arg_lst[i]
                        i += 1
                    break
                else:
                    args.append(arg)    # if no comments, args is everything
        return (addr, instr, bytes, opcode, args, remainder.strip())

    def scan_arm_instruction(self, line):
        """
        Parses a line of text which contains an ARM instruction.

        Example line: "   4:    b09b        sub sp, #108    ; 0x6c"

        Returns a tuple of:
            - Memory address of the instruction (addr = 4)
            - Hex machine code of the instruction (instr = b09b)
            - Size of the instruction (bytes = 2)
            - Opcode (opcode = 'sub')
            - Arguments (args = ['sp,', '#108'])
            - Comments (comments = '0x6c')
        """
        # Semicolon indicates comment at the end
        comments = ''
        if (line.find(';') != -1):
            comments = line[(line.find(';') + 1):].strip()
            line = line[:line.find(';')]
        # Split the rest of the line by spaces, colons, tabs, and commas
        lin_split = re.split(r'[:\t,]', line)
        lin_split[:] = [str(x).strip() for x in lin_split if str(x) != '']
        # Memory location of instruction
        addr = lin_split[0]
        # Machine code (hex) gives instruction size
        instr = lin_split[1]
        # Opcode
        opcode = lin_split[2]
        # Arguments are anything remaining (comments stripped above)
        args = lin_split[3:]

        instr = instr.replace(' ', '')  # get rid of whitespace in instruction
        bytes = len(instr)/2
        return (addr, instr, bytes, opcode, args, comments)

    def scan_rviar_instruction(self, line):
        """
        Parses a line of text which contains an IAR instruction.

        Example line: "   200003D6    4454       c.lw      a3, 0xC(s0)"

        Returns a tuple of:
            - Memory address of the instruction
            - Hex machine code of the instruction
            - Size of the instruction
            - Disassembly of machine code
            - Disassembly comments
        """
        lin_split = re.split(r'[ \t,]', line)
        lin_split[:] = [str(x).strip() for x in lin_split if str(x) != '']
        # Memory location of instruction
        addr = lin_split[0]
        # Machine code (hex) gives instruction size
        instr = lin_split[1]
        bytes = len(instr)/2
        # Opcode (lw, beqz, etc.)
        opcode = lin_split[2]
        # Args and comments more complicated since not always present/uniform
        args = []
        # ret has no additional inputs
        if (opcode != 'ret'):
            arg_lst = lin_split[3:]
            num_args = len(arg_lst)
            for i in range(num_args):
                args.append(arg_lst[i])
        return (addr, instr, bytes, opcode, args)
