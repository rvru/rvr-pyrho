"""
Parser Class for Disassembly

The ParseRules class determines the start/end of functions as well as extracts
data from parsed lines.

Author: Jennifer Hellar (jennifer.hellar@rice.edu)

"""


import re
from constants import *
import excel


class ParseRules:
    def __init__(self, compiler, benchmark):
        self.benchmark = benchmark
        self.compiler = compiler
        # Define first and last functions to parse for each compiler
        if (self.benchmark == 'WatermanBenchmark'):
            self.FIRST_RV_FUNCTION = 'main'
            self.FIRST_ARM_FUNCTION = 'strlen'
            self.FIRST_IAR_FUNCTION = 'main'
            self.LAST_RV_FUNCTION = 'strlen'
            self.LAST_ARM_FUNCTION = 'main'
            self.LAST_IAR_FUNCTION = 'strlen'

        elif (self.benchmark == 'fir_filter'):
            self.FIRST_RV_FUNCTION = 'main'
            self.FIRST_ARM_FUNCTION = 'main'
            self.FIRST_IAR_FUNCTION = 'main'
            self.LAST_RV_FUNCTION = 'main'
            self.LAST_ARM_FUNCTION = 'main'
            self.LAST_IAR_FUNCTION = 'main'

        elif (self.benchmark == 'aha_mont64'):
            self.FIRST_RV_FUNCTION = 'mulul64'
            self.FIRST_ARM_FUNCTION = 'mulul64'
            self.FIRST_IAR_FUNCTION = 'mulul64'
            self.LAST_RV_FUNCTION = 'benchmark_body'
            self.LAST_ARM_FUNCTION = 'benchmark_body'
            self.LAST_IAR_FUNCTION = 'benchmark_body'

        elif (self.benchmark == 'crc32'):
            self.FIRST_RV_FUNCTION = 'crc32pseudo'
            self.FIRST_ARM_FUNCTION = 'crc32pseudo'
            self.FIRST_IAR_FUNCTION = 'crc32pseudo'
            self.LAST_RV_FUNCTION = 'benchmark_body'
            self.LAST_ARM_FUNCTION = 'benchmark_body'
            self.LAST_IAR_FUNCTION = 'benchmark_body'

        elif (self.benchmark == 'cubic'):
            self.FIRST_RV_FUNCTION = 'benchmark_body'
            self.FIRST_ARM_FUNCTION = 'benchmark_body'
            self.FIRST_IAR_FUNCTION = 'benchmark_body'
            self.LAST_RV_FUNCTION = 'SolveCubic'
            self.LAST_ARM_FUNCTION = 'SolveCubic'
            self.LAST_IAR_FUNCTION = 'SolveCubic'

        elif (self.benchmark == 'edn'):
            self.FIRST_RV_FUNCTION = 'vec_mpy1'
            self.FIRST_ARM_FUNCTION = 'vec_mpy1'
            self.FIRST_IAR_FUNCTION = 'vec_mpy1'
            self.LAST_RV_FUNCTION = 'benchmark_body'
            self.LAST_ARM_FUNCTION = 'benchmark_body'
            self.LAST_IAR_FUNCTION = 'benchmark_body'

        elif (self.benchmark == 'huffbench'):
            self.FIRST_RV_FUNCTION = 'heap_adjust'
            self.FIRST_ARM_FUNCTION = 'heap_adjust'
            self.FIRST_IAR_FUNCTION = 'heap_adjust'
            self.LAST_RV_FUNCTION = 'benchmark_body'
            self.LAST_ARM_FUNCTION = 'benchmark_body'
            self.LAST_IAR_FUNCTION = 'benchmark_body'

        elif (self.benchmark == 'matmult_int'):
            self.FIRST_RV_FUNCTION = 'Multiply'
            self.FIRST_ARM_FUNCTION = 'Multiply'
            self.FIRST_IAR_FUNCTION = 'Multiply'
            self.LAST_RV_FUNCTION = 'benchmark_body'
            self.LAST_ARM_FUNCTION = 'benchmark_body'
            self.LAST_IAR_FUNCTION = 'benchmark_body'

        elif (self.benchmark == 'minver'):
            self.FIRST_RV_FUNCTION = 'minver_fabs'
            self.FIRST_ARM_FUNCTION = 'minver_fabs'
            self.FIRST_IAR_FUNCTION = 'minver_fabs'
            self.LAST_RV_FUNCTION = 'benchmark_body'
            self.LAST_ARM_FUNCTION = 'benchmark_body'
            self.LAST_IAR_FUNCTION = 'benchmark_body'

        elif (self.benchmark == 'nbody'):
            self.FIRST_RV_FUNCTION = 'offset_momentum'
            self.FIRST_ARM_FUNCTION = 'offset_momentum'
            self.FIRST_IAR_FUNCTION = 'offset_momentum'
            self.LAST_RV_FUNCTION = 'benchmark_body'
            self.LAST_ARM_FUNCTION = 'benchmark_body'
            self.LAST_IAR_FUNCTION = 'benchmark_body'

        elif (self.benchmark == 'nettle_aes'):
            self.FIRST_RV_FUNCTION = '_aes_set_key'
            self.FIRST_ARM_FUNCTION = '_aes_set_key'
            self.FIRST_IAR_FUNCTION = '_aes_set_key'
            self.LAST_RV_FUNCTION = 'benchmark_body'
            self.LAST_ARM_FUNCTION = 'benchmark_body'
            self.LAST_IAR_FUNCTION = 'benchmark_body'

        elif (self.benchmark == 'nettle_sha256'):
            self.FIRST_RV_FUNCTION = 'sha256_init'
            self.FIRST_ARM_FUNCTION = '_nettle_write_be32'
            self.FIRST_IAR_FUNCTION = 'sha256_init'
            self.LAST_RV_FUNCTION = 'benchmark_body'
            self.LAST_ARM_FUNCTION = 'benchmark_body'
            self.LAST_IAR_FUNCTION = 'benchmark_body'

        elif (self.benchmark == 'nsichneu'):
            self.FIRST_RV_FUNCTION = 'benchmark_body'
            self.FIRST_ARM_FUNCTION = 'benchmark_body'
            self.FIRST_IAR_FUNCTION = 'benchmark_body'
            self.LAST_RV_FUNCTION = 'benchmark_body'
            self.LAST_ARM_FUNCTION = 'benchmark_body'
            self.LAST_IAR_FUNCTION = 'benchmark_body'

        elif (self.benchmark == 'picojpeg'):
            self.FIRST_RV_FUNCTION = 'pjpeg_need_bytes_callback'
            self.FIRST_ARM_FUNCTION = 'pjpeg_need_bytes_callback'
            self.FIRST_IAR_FUNCTION = 'pjpeg_need_bytes_callback'
            self.LAST_RV_FUNCTION = 'pjpeg_decode_init'
            self.LAST_ARM_FUNCTION = 'pjpeg_decode_init'
            self.LAST_IAR_FUNCTION = 'pjpeg_decode_init'

        elif (self.benchmark == 'qrduino'):
            self.FIRST_RV_FUNCTION = 'modnn'
            self.FIRST_ARM_FUNCTION = 'modnn'
            self.FIRST_IAR_FUNCTION = 'modnn'
            self.LAST_RV_FUNCTION = 'benchmark_body'
            self.LAST_ARM_FUNCTION = 'benchmark_body'
            self.LAST_IAR_FUNCTION = 'benchmark_body'

        elif (self.benchmark == 'sglib_combined'):
            self.FIRST_RV_FUNCTION = 'sglib___rbtree_fix_left_insertion_discrepancy'
            self.FIRST_ARM_FUNCTION = 'sglib_dllist_add'
            self.FIRST_IAR_FUNCTION = 'sglib___rbtree_fix_left_insertion_discrepancy'
            self.LAST_RV_FUNCTION = 'benchmark_body'
            self.LAST_ARM_FUNCTION = 'benchmark_body'
            self.LAST_IAR_FUNCTION = 'benchmark_body'

        elif (self.benchmark == 'slre'):
            self.FIRST_RV_FUNCTION = 'op_len'
            self.FIRST_ARM_FUNCTION = 'op_len'
            self.FIRST_IAR_FUNCTION = 'op_len'
            self.LAST_RV_FUNCTION = 'benchmark_body'
            self.LAST_ARM_FUNCTION = 'benchmark_body'
            self.LAST_IAR_FUNCTION = 'benchmark_body'

        elif (self.benchmark == 'st'):
            self.FIRST_RV_FUNCTION = 'InitSeed'
            self.FIRST_ARM_FUNCTION = 'Square'
            self.FIRST_IAR_FUNCTION = 'InitSeed'
            self.LAST_RV_FUNCTION = 'benchmark_body'
            self.LAST_ARM_FUNCTION = 'benchmark_body'
            self.LAST_IAR_FUNCTION = 'benchmark_body'

        elif (self.benchmark == 'statemate'):
            self.FIRST_RV_FUNCTION = 'interface'
            self.FIRST_ARM_FUNCTION = 'interface'
            self.FIRST_IAR_FUNCTION = 'interface'
            self.LAST_RV_FUNCTION = 'benchmark_body'
            self.LAST_ARM_FUNCTION = 'benchmark_body'
            self.LAST_IAR_FUNCTION = 'benchmark_body'

        elif (self.benchmark == 'ud'):
            self.FIRST_RV_FUNCTION = 'ludcmp'
            self.FIRST_ARM_FUNCTION = 'ludcmp'
            self.FIRST_IAR_FUNCTION = 'ludcmp'
            self.LAST_RV_FUNCTION = 'benchmark_body'
            self.LAST_ARM_FUNCTION = 'benchmark_body'
            self.LAST_IAR_FUNCTION = 'benchmark_body'

        elif (self.benchmark == 'wikisort'):
            self.FIRST_RV_FUNCTION = 'TestCompare'
            self.FIRST_ARM_FUNCTION = 'Min'
            self.FIRST_IAR_FUNCTION = 'TestCompare'
            self.LAST_RV_FUNCTION = 'benchmark_body'
            self.LAST_ARM_FUNCTION = 'benchmark_body'
            self.LAST_IAR_FUNCTION = 'benchmark_body'

    def is_first(self, line):
        """
        Returns TRUE if input line is the initialization of the first function
        to parse.
        """
        res = None
        if (self.compiler == 'rvgcc'):
            res = (re.search(self.FIRST_RV_FUNCTION, line) is not None) \
                and self.is_func_start(line)
        elif (self.compiler == 'armcc'):
            res = (re.search(self.FIRST_ARM_FUNCTION, line) is not None) \
                and self.is_func_start(line)
        elif (self.compiler == 'armclang'):
            res = (re.search(self.FIRST_ARM_FUNCTION, line) is not None) \
                and self.is_func_start(line)
        elif (self.compiler == 'armgcc'):
            res = (re.search(self.FIRST_ARM_FUNCTION, line) is not None) \
                and self.is_func_start(line)
        elif (self.compiler == 'IAR'):
            res = (re.search(self.FIRST_IAR_FUNCTION, line) is not None) \
                and self.is_func_start(line)
        return res

    def is_last(self, line):
        """
        Returns TRUE if input line is the initialization of the last function
        to parse.
        """
        if (self.compiler == 'rvgcc'):
            res = (re.search(self.LAST_RV_FUNCTION, line) is not None) \
                and self.is_func_start(line)
        elif (self.compiler == 'armcc'):
            res = (re.search(self.LAST_ARM_FUNCTION, line) is not None) \
                and self.is_func_start(line)
        elif (self.compiler == 'armclang'):
            res = (re.search(self.LAST_ARM_FUNCTION, line) is not None) \
                and self.is_func_start(line)
        elif (self.compiler == 'armgcc'):
            res = (re.search(self.LAST_ARM_FUNCTION, line) is not None) \
                and self.is_func_start(line)
        elif (self.compiler == 'IAR'):
            res = (re.search(self.LAST_IAR_FUNCTION, line) is not None) \
                and self.is_func_start(line)
        return res

    def is_func_start(self, line):
        """ Returns TRUE if input line is the initialization of a function. """
        res = None
        if (self.compiler == 'IAR'):
            res = re.search(r'^\s\s\?*`*[a-zA-Z_]\w+`*:', line)
        # elif (self.compiler == 'armclang'):
        #     res = re.search(r'^\w+\s<__arm_cp.+>:', line)
        #     if (res is not None):
        #         res = None
        #     else:
        #         res = re.search(r'^\w+\s<.+>:', line)
        else:
            res = re.search(r'^\w+\s<.+>:', line)
        return (res is not None)

    def is_func_end(self, line):
        """
        Returns TRUE if input line is the end of a function during parsing.
        """
        # Check if new function or empty line
        # Check if $d (data) or $t (table) section (IAR only)
        res = self.is_func_start(line) \
            or line.strip() == '' \
            or ((re.search(r'^\s\s`*[$a-zA-Z_][d.]*\w+`*:', line) is not None)
                and self.compiler == 'IAR')
        return res

    def is_end(self, line):
        """
        Returns TRUE if input line is the end of the last function to parse.
        """
        res = (line.strip() == '...')
        return res

    def is_skippable(self, line):
        """
        Returns TRUE if input line should not be parsed (data or empty).
        """
        res = (line.find('.word') != -1) or (line.find('.short') != -1) \
            or (line.strip() == '') or (line.find('.text') != -1) \
            or (line.find('.iar') != -1) or (line.find('Region') != -1) \
            or (line.find('...') != -1) \
            or (line.find('file format') != -1) \
            or (line.find('Disassembly') != -1)
            # or (line.find('__arm_cp') != -1 and line.find('>:') != -1)
        return res

    def get_func_data(self, line):
        """
        Parses a line of text which contains a function initialization.

        Example line: "00000000 <com_usb_pd_initialize>:"

        Returns a tuple of:
            - full name (com_usb_pd_initialize)
            - short name (initialize) suitable for naming an Excel worksheet
        """
        lin_split = re.split(' ', line)
        lin_split[:] = [str(x).strip() for x in lin_split if str(x) != '']

        full_name = ''
        name = None
        # Choose functions to parse and generate wksheet names (<31 char)
        if (self.compiler == 'rvgcc'):
            # Function name
            full_name = lin_split[1]
            # Exclude extra characters <>:
            full_name = full_name[1:-2]
            if len(full_name) > 30:
                name = full_name[-31:]
            else:
                name = full_name
            # These are the same for any benchmark
            if (save_restore_en):
                if (full_name[0:12] == '__riscv_save'):
                    name = '__riscv_save'
                elif (full_name[0:15] == '__riscv_restore'):
                    name = '__riscv_restore'
            excel.wksheet_names[full_name] = name
        elif (self.compiler == 'rviar'):
            full_name = lin_split[0]
            # Exclude '??' and ':' as needed
            full_name = full_name[:-1]
            if full_name[:2] == '??':
                full_name = full_name[2:]
            if full_name in excel.wksheet_names.keys():
                name = excel.wksheet_names[full_name]
            elif (save_restore_en):
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

    def scan_iar_instruction(self, line):
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
