
"""
Program Constants

This file defines all of the constant variables used throughout the program.

Author: Jennifer Hellar (jennifer.hellar@rice.edu)

"""
SOURCES = ['hydra']
BENCHMARKS = ['WatermanBenchmark', 'fir_filter',
    'aha_mont64', 'crc32', 'cubic', 'edn', 'huffbench', 'matmult_int',
    'minver', 'nbody', 'nettle_aes', 'nettle_sha256', 'nsichneu', 'picojpeg',
    'qrduino', 'sglib_combined', 'slre', 'st', 'statemate', 'ud', 'wikisort']

IAR = False

""" Enable Desired Compact Instructions """
lwpc_en = ('cx.lwpc', True)

ld_str_en = True
sb_en = ('cx.sb', ld_str_en)
sh_en = ('cx.sh', ld_str_en)
lbu_en = ('cx.lbu', ld_str_en)
lhu_en = ('cx.lhu', ld_str_en)
lb_en = ('cx.lb', ld_str_en)
lh_en = ('cx.lh', ld_str_en)

addi_subi_en = True
addi8 = ('cx.addi8', addi_subi_en)
addi5 = ('cx.addi5', addi_subi_en)
subi8 = ('cx.subi8', addi_subi_en)
subi5 = ('cx.subi5', addi_subi_en)

slli_en = ('cx.slli', True)

branches_en = True
BR_KEEP = 0.9
bne_en = ('cx.bne', branches_en)
blt_en = ('cx.blt', branches_en)
bge_en = ('cx.bge', branches_en)
branches = [bne_en, blt_en, bge_en]
BR_ENABLED = [i[0] for i in branches if (i[1] is True)]

str_zero_en = False
swzero_en = ('cx.swzero', str_zero_en)
shzero_en = ('cx.shzero', str_zero_en)
sbzero_en = ('cx.sbzero', str_zero_en)

# NOTE: j_jal_en and save_restore_en cannot both be True
j_jal_en = True
j_en = ('c.j (restore)', j_jal_en)
jal_en = ('c.jal (save)', j_jal_en)

save_restore_en = False
push_en = ('push (save)', save_restore_en)
pop_en = ('pop (restore)', save_restore_en)

en_lst = [lwpc_en, sb_en, sh_en, lbu_en, lhu_en, lb_en, lh_en, addi5,
          subi5, addi8, subi8, slli_en, bne_en, blt_en, bge_en,
          swzero_en, shzero_en, sbzero_en, j_en, jal_en, push_en, pop_en]
ENABLED = [i[0] for i in en_lst if (i[1] is True)]
IGNORE_REGS = False

""" Enable Desired Fused Pair Instructions """
lw_jalr_en = (('c.lw', 'c.jalr'), False)
lw_li_en = (('c.lw', 'c.li'), False)

# Load/load
lw16_lw16_en = (('c.lw', 'c.lw'), False)
lw32_lw16_en = (('lw', 'c.lw'), False)
lw16_lw32_en = (('c.lw', 'lw'), False)
lw32_lw32_en = (('lw', 'lw'), False)
# Store/store
sw16_sw16_en = (('c.sw', 'c.sw'), False)
sw32_sw16_en = (('sw', 'c.sw'), False)
sw16_sw32_en = (('c.sw', 'sw'), False)
sw32_sw32_en = (('sw', 'sw'), False)
# Load/store
lw16_sw16_en = (('c.lw', 'c.sw'), False)
sw16_lw16_en = (('c.sw', 'c.lw'), False)
sw32_lw32_en = (('sw', 'lw'), False)
# Move/move
mv_mv_en = (('c.mv', 'c.mv'), False)
sw_mv_en = (('c.sw', 'c.mv'), False)

pair_en_lst = [lw_jalr_en, lw_li_en, lw16_lw16_en, lw32_lw16_en, lw16_lw32_en,
               lw32_lw32_en, sw16_sw16_en, sw32_sw16_en, sw16_sw32_en,
               sw32_sw32_en, lw16_sw16_en, sw16_lw16_en, sw32_lw32_en,
               mv_mv_en, sw_mv_en]
PAIRS_ENABLED = [i[0] for i in pair_en_lst if (i[1] is True)]

# Allowed register list for compact instructions
REG_LIST = ['s0', 's1', 'a0', 'a1', 'a2', 'a3', 'a4', 'a5']

""" Define states for parsing assembly """
S_INIT = "STATE: INITIAL"
S_FIRST = "STATE: FIRST FUNCTION"
S_FUNC_START = "STATE: NEW FUNCTION"
S_FUNC_PARSE = "STATE: PARSING"
S_FUNC_END = "STATE: FUNCTION END"
S_WAIT = "STATE: WAIT BETWEEN FUNCTIONS"
S_LAST = "STATE: LAST FUNCTION"
S_END = "STATE: END"

""" Define Instruction Formats and Mappings """

# Defines the 6 recognized types of instruction formats recognized (I split)
RV32_FORMATS = ['R', 'I-OP', 'U', 'I-LD', 'S', 'B', 'J', 'I-CSR', 'I-ENV']

# Track what category each RISC-V 32-bit opcode falls under
RV32_INSTR_FORMATS = {
    # Base Integer Instructions (RV32I)
    'sll':      ['R'],
    'slli':     ['I-OP'],
    'srl':      ['R'],
    'srli':     ['I-OP'],
    'sra':      ['R'],
    'srai':     ['I-OP'],
    'add':      ['R'],
    'addi':     ['I-OP'],
    'sub':      ['R'],
    'auipc':    ['U'],
    'lui':      ['U'],
    'xor':      ['R'],
    'xori':     ['I-OP'],
    'or':       ['R'],
    'ori':      ['I-OP'],
    'and':      ['R'],
    'andi':     ['I-OP'],
    'slt':      ['R'],
    'slti':     ['I-OP'],
    'sltu':     ['R'],
    'sltiu':    ['I-OP'],
    'beq':      ['B'],
    'bne':      ['B'],
    'blt':      ['B'],
    'bge':      ['B'],
    'bltu':     ['B'],
    'bgeu':     ['B'],
    'jal':      ['J'],
    'jalr':     ['I-OP'],
    'fence':    ['I-OP'],
    'fence.i':  ['I-OP'],
    'ecall':    ['I-ENV'],
    'ebreak':   ['I-ENV'],
    'csrrw':    ['I-CSR'],
    'csrrs':    ['I-CSR'],
    'csrrc':    ['I-CSR'],
    'csrrwi':   ['I-CSR'],
    'csrrsi':   ['I-CSR'],
    'csrrci':   ['I-CSR'],
    'lb':       ['I-LD'],
    'lh':       ['I-LD'],
    'lbu':      ['I-LD'],
    'lhu':      ['I-LD'],
    'lw':       ['I-LD'],
    'sb':       ['S'],
    'sh':       ['S'],
    'sw':       ['S'],
    # Multiply-Divide Instruction Extention (RV32M)
    'mul':      ['R'],
    'mulh':     ['R'],
    'mulhsu':   ['R'],
    'mulhu':    ['R'],
    'div':      ['R'],
    'divu':     ['R'],
    'rem':      ['R'],
    'remu':     ['R'],
    # pseudoinstructions (not a complete listing)
    'nop':      ['addi'],
    'li':       ['addi'],
    'li12':     ['addi'],
    'mv':       ['addi'],
    'not':      ['xori'],
    'neg':      ['sub'],
    'seqz':     ['sltiu'],
    'snez':     ['sltu'],
    'sltz':     ['slt'],
    'sgtz':     ['slt'],
    'bgt':      ['blt'],
    'ble':      ['bge'],
    'bgtu':     ['bltu'],
    'bleu':     ['bgeu'],
    'beqz':     ['beq'],
    'bnez':     ['bne'],
    'blez':     ['bge'],
    'bgez':     ['bge'],
    'bltz':     ['blt'],
    'bgtz':     ['blt'],
    'j':        ['jal'],
    'jr':       ['jalr'],
    'ret':      ['jalr'],
    'call20':   ['auipc', 'jalr'],
    'csrr':     ['csrrs'],
    'csrw':     ['csrrw'],
    'csrs':     ['csrrs'],
    'csrc':     ['csrrc'],
    'csrwi':    ['csrrwi'],
    'csrsi':    ['csrrsi'],
    'csrci':    ['csrrci'],
}

RV32C_FORMATS = ['CR', 'CI', 'CSS', 'CIW', 'CL', 'CS', 'CB', 'CJ']

RV32C_INSTR_FORMATS = {
    'c.lwsp':       ['CI'],
    'c.swsp':       ['CSS'],
    'c.lw':         ['CL'],
    'c.sw':         ['CS'],
    'c.j':          ['CJ'],
    'c.jal':        ['CJ'],
    'c.jr':         ['CR'],
    'c.jalr':       ['CR'],
    'c.beqz':       ['CB'],
    'c.bnez':       ['CB'],
    'c.li':         ['CI'],
    'c.lui':        ['CI'],
    'c.addi':       ['CI'],
    'c.addi16sp':   ['CI'],
    'c.slli':       ['CI'],
    'c.mv':         ['CR'],
    'c.add':        ['CR'],
    'c.sub':        ['CR'],
    'c.nop':        ['CI'],
    'c.ebreak':     ['CR']
    # pseudoinstructions
}

""" Define Excel options """

# IMPORTANT: All table names must be unique (dictionary keys in excel.py)

# Table titles for the Summary page
SUMMARY_TOTALS_TABLE = 'Benchmark Performance (RISC-V vs. ARM)'
SUMMARY_MAIN_TABLE = 'Function Sizes (bytes)'

SUMMARY_INSTR_TABLE = 'Compressed Extension Reductions'
SUMMARY_RULES_TABLE = 'Compressed Extension Rules'

SUMMARY_RVGCC_INSTR_TOT_TABLE = 'rvgcc instructions'
# SUMMARY_IAR_INSTR_TOT_TABLE = 'IAR Instructions'

SUMMARY_RVGCC_PAIRS_TABLE = 'rvgcc instruction pairs'
# SUMMARY_IAR_PAIRS_TABLE = 'IAR Instruction Pairs'

SUMMARY_RVGCC_OVERSHOOT_TABLE = 'Overshoot (rvgcc - ARM)'
# SUMMARY_IAR_OVERSHOOT_TABLE = 'Overshoot (IAR - ARM)'

# Table titles for the __riscv_save, __riscv_restore pages
# SAVE_IAR_TOTALS_TABLE = 'RISC-V (IAR) Save Totals'
# SAVE_IAR_A_TABLE = 'save_0 - save_3 (IAR)'
# SAVE_IAR_B_TABLE = 'save_4 - save_7 (IAR)'
# SAVE_IAR_C_TABLE = 'save_8 - save_11 (IAR)'
# SAVE_IAR_D_TABLE = 'save_12 (IAR)'
# iar_save_tables = [SAVE_IAR_A_TABLE, SAVE_IAR_B_TABLE, SAVE_IAR_C_TABLE,
#                    SAVE_IAR_D_TABLE]
SAVE_RVGCC_TOTALS_TABLE = 'RISC-V Save Totals'
SAVE_RVGCC_A_TABLE = 'save_0 - save_3'
SAVE_RVGCC_B_TABLE = 'save_4 - save_7'
SAVE_RVGCC_C_TABLE = 'save_8 - save_11'
SAVE_RVGCC_D_TABLE = 'save_12'
rvgcc_save_tables = [SAVE_RVGCC_A_TABLE, SAVE_RVGCC_B_TABLE,
                     SAVE_RVGCC_C_TABLE, SAVE_RVGCC_D_TABLE]

# RESTORE_IAR_TOTALS_TABLE = 'RISC-V (IAR) Restore Totals'
# RESTORE_IAR_A_TABLE = 'restore_0 - restore_3 (IAR)'
# RESTORE_IAR_B_TABLE = 'restore_4 - restore_7 (IAR)'
# RESTORE_IAR_C_TABLE = 'restore_8 - restore_11 (IAR)'
# RESTORE_IAR_D_TABLE = 'restore_12 (IAR)'
# iar_restore_tables = [RESTORE_IAR_A_TABLE, RESTORE_IAR_B_TABLE,
#                       RESTORE_IAR_C_TABLE, RESTORE_IAR_D_TABLE]
RESTORE_RVGCC_TOTALS_TABLE = 'RISC-V Restore Totals'
RESTORE_RVGCC_A_TABLE = 'restore_0 - restore_3'
RESTORE_RVGCC_B_TABLE = 'restore_4 - restore_7'
RESTORE_RVGCC_C_TABLE = 'restore_8 - restore_11'
RESTORE_RVGCC_D_TABLE = 'restore_12'
rvgcc_restore_tables = [RESTORE_RVGCC_A_TABLE, RESTORE_RVGCC_B_TABLE,
                        RESTORE_RVGCC_C_TABLE, RESTORE_RVGCC_D_TABLE]

# Table titles for the function pages
ARM_TOTALS_TABLE = 'ARM M0+ Totals'
ARM_TABLE = 'ARM M0+'

# IAR_TOTALS_TABLE = 'RISC-V (IAR) Totals)'
# IAR_TABLE = 'RISC-V (IAR)'

RVGCC_TOTALS_TABLE = 'RISC-V Totals'
RVGCC_TABLE = 'RISC-V'

RVGCC_BITS_TABLE = 'RISC-V Offset Bits'
# IAR_BITS_TABLE = 'IAR Offset Bits'

RVGCC_INSTR_TABLE = 'RISC-V Instructions'
# IAR_INSTR_TABLE = 'IAR Instructions'

# Create dictionaries for mapping Excel grid (A-BZ columns, 1000 rows):
#    CELL_NAME: row, col map to cell e.g. (0, 1) --> 'A2'
#    CELL_COORD: cell map to row, col e.g. 'B6' --> (1, 5)
CELL_NAME = {}
CELL_COORD = {}
for row in range(10001):
    for col in range(1, 27):  # A-Z
        CELL_NAME[(row, col - 1)] = chr(col+64) + str(row + 1)
        CELL_COORD[chr(col+64) + str(row + 1)] = (row, col - 1)
    for col in range(27, 53):  # AA-AZ
        CELL_NAME[(row, col - 1)] = 'A' + chr(col - 26 + 64) + str(row + 1)
        CELL_COORD['A' + chr(col - 26 + 64) + str(row + 1)] = (row, col - 1)
    for col in range(53, 79):  # BA-BZ
        CELL_NAME[(row, col - 1)] = 'B' + chr(col - 52 + 64) + str(row + 1)
        CELL_COORD['B' + chr(col - 52 + 64) + str(row + 1)] = (row, col - 1)

# Create dictionary of Excel cell formats (to be added to the workbook)
# Color codes: https://www.rapidtables.com/web/color/blue-color.html
teal = '#008080'
light_cyan = '#E0FFFF'
sky_blue = '#87CEEB'
gold = '#FFD700'
orange = '#FFA500'
XLS_FORMATS = {'header':
               {'bold': True, 'font_color': 'white', 'bg_color': teal,
                'border': 1,  'font_size': 13},

               'gold_header':
               {'bold': True, 'font_color': gold,    'bg_color': teal,
                'border': 1,  'font_size': 13},

               'red_header':
               {'bold': True, 'font_color': 'red',   'bg_color': teal,
                'border': 1,  'font_size': 13},

               'title':
               {'bold': True, 'font_color': 'white', 'bg_color': teal,
                'border': 1,  'font_size': 13},

               'light_bg':
               {'bold': False,                       'bg_color': light_cyan,
                'border': 1},

               'dark_bg':
               {'bold': False,                       'bg_color': sky_blue,
                'border': 1},

               'gold_bg':
               {'bold': False,                       'bg_color': gold,
                'border': 1},

               'bold_light':
               {'bold': True,                        'bg_color': light_cyan,
                'border': 1},

               'bold_dark':
               {'bold': True,                        'bg_color': sky_blue,
                'border': 1},

               'gold_light':
               {'bold': True, 'font_color': gold,    'bg_color': light_cyan,
                'border': 1},

               'red':
               {'bold': True, 'font_color': 'red'},

               'red_light':
               {'bold': True, 'font_color': 'red',   'bg_color': light_cyan,
                'border': 1},

               'red_dark':
               {'bold': True, 'font_color': 'red',   'bg_color': sky_blue,
                'border': 1},

               'green':
               {'bold': True, 'font_color': 'green'},

               'green_light':
               {'bold': True, 'font_color': 'green', 'bg_color': light_cyan,
                'border': 1},

               'green_dark':
               {'bold': True, 'font_color': 'green', 'bg_color': sky_blue,
                'border': 1},

               'percent':
               {'bold': True, 'font_color': 'black', 'bg_color': light_cyan,
                'border': 1,  'num_format': '0.00%'},

               'red_light_percent':
               {'bold': True, 'font_color': 'red',   'bg_color': light_cyan,
                'border': 1,  'num_format': '0.00%'},

               'green_light_percent':
               {'bold': True, 'font_color': 'green', 'bg_color': light_cyan,
                'border': 1,  'num_format': '0.00%'},

               'orange_bg':
               {'bold': False,                        'bg_color': orange,
                'border': 1},

               'orange_header':
               {'bold': True, 'font_color': orange,   'bg_color': teal,
                'border': 1,  'font_size': 13},

               'orange_light':
               {'bold': True, 'font_color': orange,   'bg_color': light_cyan,
                'border': 1}
               }
