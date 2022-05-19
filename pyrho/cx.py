"""
Compact Instruction Evaluation

This file contains all the functions for determining if 32-bit instructions
can be replaced by user-defined 32-bit or 16-bit instructions.  Replaceable
instructions should be enabled in constants.py.

Author: Jennifer Hellar

"""

import math
# Enabled replacement instructions
from constants import ENABLED
# Allowed src/dest registers for custom compressed instructions
from constants import REG_LIST

from constants import IGNORE_REGS


def get_regs_and_offset(opcode, args):
    """ Decompose the arguments of a RISC-V instruction. """
    if (opcode == 'lw') or (opcode == 'lbu') or (opcode == 'lhu') or\
            (opcode == 'lb') or (opcode == 'lh'):
        # e.g. lw   a5,-1816(gp) # 127f4
        rd = args[0]
        args = args[1]
        args = args.split('(')
        offset = args[0]
        rs1 = args[1]
        rs1 = rs1[:-1]  # Exclude final ")"
        return (rd, rs1, offset)
    if (opcode == 'sb') or (opcode == 'sh') or (opcode == 'swzero') or\
            (opcode == 'shzero') or (opcode == 'sbzero'):
        rs2 = args[0]
        args = args[1]
        args = args.split('(')
        offset = args[0]
        rs1 = args[1]
        rs1 = rs1[:-1]  # Exclude final ")"
        return (rs2, rs1, offset)
    if (opcode == 'addi'):
        rd = args[0]
        rs1 = args[1]
        offset = args[2]
        return (rd, rs1, offset)
    if (opcode == 'c.addi'):
        rd = args[0]
        rs1 = args[1]
        offset = args[2]
        return (rd, rs1, offset)
    if (opcode == 'slli'):
        rd = args[0]
        rs1 = args[1]
        offset = args[2]
        return (rd, rs1, offset)
    if (opcode == 'j'):
        # offset only
        rs2 = None
        rs1 = None
        offset = args[0]
        return (rs2, rs1, offset)
    if (opcode == 'jal'):
        # offset and one register
        rd = args[0]
        offset = args[1]
        rs1 = None
        return (rd, rs1, offset)
    if (opcode == 'bne'):
        rs2 = args[0]
        rs1 = args[1]
        offset = args[2]
        return (rs2, rs1, offset)
    if (opcode == 'beq'):
        rs2 = args[0]
        rs1 = args[1]
        offset = args[2]
        return (rs2, rs1, offset)
    if (opcode == 'blt'):
        rs2 = args[0]
        rs1 = args[1]
        offset = args[2]
        return (rs2, rs1, offset)
    if (opcode == 'bge'):
        rs2 = args[0]
        rs1 = args[1]
        offset = args[2]
        return (rs2, rs1, offset)


def is_lw_replaceable(args, curr_max, curr_min):
    """
    Checks if 32-bit LW instruction replaceable by 16-bit lwpc instruction.

    Note: this only checks the registers and updates the current max/min offset
    values. To know if it can be replaced, you must look at overall number of
    bits to encode the offsets for the function (see check_offsets()).

    Returns a tuple of:
        - res: True/False after checking registers
        - (rd, rs1, offset) of the instruction
        - curr_max: updated max LW offset for the function
        - curr_min: updated min LW offset for the function
    """
    res = False
    (rd, rs1, offset) = get_regs_and_offset('lw', args)
    # Check registers
    if (rs1 == 'gp') and (IGNORE_REGS or rd in REG_LIST):
        res = True
        # Update offsets
        if (offset.find('0x') != -1):
            offset = int(offset, 16)
        offset = abs(int(offset))
        if(offset > curr_max):
            curr_max = offset
            if (curr_min == float("inf")):
                curr_min = curr_max
        elif (offset < curr_min):
            curr_min = offset
    return (res, (rd, rs1, offset), curr_max, curr_min)


def is_sb_replaceable(args):
    """
    Checks if a 32-bit SB instruction can be replaced with a 16-bit SB.

    Returns a tuple of:
        - res: True/False after checking registers and offset size
        - (rs2, rs1, offset) of the instruction
        - type_code: cx.sb or cx.sbzero
    """
    res = False
    type_code = ''
    (rs2, rs1, offset) = get_regs_and_offset('sb', args)
    regs_okay = IGNORE_REGS or ((rs1 in REG_LIST) and (rs2 in REG_LIST))
    if (offset.find('0x') != -1):
        offset = int(offset, 16)
    offset_okay = (abs(int(offset)) < 32) and (int(offset) >= 0)
    # Check registers, offset, and compressed instruction ENABLED
    if (regs_okay) and (offset_okay) and ('cx.sb' in ENABLED):
        res = True
        type_code = 'cx.sb'
    elif (IGNORE_REGS or rs1 in REG_LIST) and (rs2 == 'zero') and \
            (offset_okay) and ('cx.sbzero' in ENABLED):
        res = True
        type_code = 'cx.sbzero'
    return (res, (rs2, rs1, offset), type_code)


def is_sh_replaceable(args):
    """
    Checks if a 32-bit SH instruction can be replaced with a 16-bit SH.

    Returns a tuple of:
        - res: True/False after checking registers and offset size
        - (rs2, rs1, offset) of the instruction
        - type_code: cx.sh or cx.shzero
    """
    res = False
    type_code = ''
    (rs2, rs1, offset) = get_regs_and_offset('sh', args)
    regs_okay = IGNORE_REGS or ((rs1 in REG_LIST) and (rs2 in REG_LIST))
    if (offset.find('0x') != -1):
        offset = int(offset, 16)
    offset_okay = (abs(int(offset)) < 64) and (int(offset) >= 0)
    if (regs_okay) and (offset_okay) and ('cx.sh' in ENABLED):
        res = True
        type_code = 'cx.sh'
    elif (IGNORE_REGS or rs1 in REG_LIST) and (rs2 == 'zero') and \
            (offset_okay) and ('cx.shzero' in ENABLED):
        res = True
        type_code = 'cx.shzero'
    return (res, (rs2, rs1, offset), type_code)


def is_lbu_replaceable(args):
    """
    Checks if a 32-bit LBU instruction can be replaced with a 16-bit LBU.

    Returns a tuple of:
        - res: True/False after checking registers and offset size
        - (rd, rs1, offset) of the instruction
        - type_code: 'cx.lbu' or ''
    """
    res = False
    type_code = ''
    (rd, rs1, offset) = get_regs_and_offset('lbu', args)
    regs_okay = IGNORE_REGS or ((rs1 in REG_LIST) and (rd in REG_LIST))
    if (offset.find('0x') != -1):
        offset = int(offset, 16)
    offset_okay = (abs(int(offset)) < 32) and (int(offset) >= 0)
    if (regs_okay) and (offset_okay):
        res = True
        type_code = 'cx.lbu'
    return (res, (rd, rs1, offset), type_code)


def is_lhu_replaceable(args):
    """
    Checks if a 32-bit LHU instruction can be replaced with a 16-bit LHU.

    Returns a tuple of:
        - res: True/False after checking registers and offset size
        - (rd, rs1, offset) of the instruction
        - type_code: 'cx.lhu' or ''
    """
    res = False
    type_code = ''
    (rd, rs1, offset) = get_regs_and_offset('lhu', args)
    regs_okay = IGNORE_REGS or ((rs1 in REG_LIST) and (rd in REG_LIST))
    if (offset.find('0x') != -1):
        offset = int(offset, 16)
    offset_okay = (abs(int(offset)) < 64) and (int(offset) >= 0)
    if (regs_okay) and (offset_okay):
        res = True
        type_code = 'cx.lhu'
    return (res, (rd, rs1, offset), type_code)


def is_lb_replaceable(args):
    """
    Checks if a 32-bit LB instruction can be replaced with a 16-bit LB.

    Returns a tuple of:
        - res: True/False after checking registers and offset size
        - (rd, rs1, offset) of the instruction
        - type_code: 'cx.lb' or ''
    """
    res = False
    type_code = ''
    (rd, rs1, offset) = get_regs_and_offset('lb', args)
    regs_okay = IGNORE_REGS or ((rs1 in REG_LIST) and (rd in REG_LIST))
    if (offset.find('0x') != -1):
        offset = int(offset, 16)
    offset_okay = (abs(int(offset)) < 32) and (int(offset) >= 0)
    if (regs_okay) and (offset_okay):
        res = True
        type_code = 'cx.lb'
    return (res, (rd, rs1, offset), type_code)


def is_lh_replaceable(args):
    """
    Checks if a 32-bit LH instruction can be replaced with a 16-bit LH.

    Returns a tuple of:
        - res: True/False after checking registers and offset size
        - (rd, rs1, offset) of the instruction
        - type_code: 'cx.lh' or ''
    """
    res = False
    type_code = ''
    (rd, rs1, offset) = get_regs_and_offset('lh', args)
    regs_okay = IGNORE_REGS or ((rs1 in REG_LIST) and (rd in REG_LIST))
    if (offset.find('0x') != -1):
        offset = int(offset, 16)
    offset_okay = (abs(int(offset)) < 64) and (int(offset) >= 0)
    if (regs_okay) and (offset_okay):
        res = True
        type_code = 'cx.lh'
    return (res, (rd, rs1, offset), type_code)


def is_addi_replaceable(args, addr):
    """
    Checks if a 32-bit ADDI instruction can be replaced with a 16-bit ADDI.

    Returns a tuple of:
        - res: True/False after checking registers and immed size
        - (rd, rs1, immed) of the instruction
        - type_code: 'cx.addi8', 'cx.addi5', 'cx.subi8', 'cx.subi5', ''
    """
    res = False
    type_code = ''
    (rd, rs1, offset) = get_regs_and_offset('addi', args)
    if (offset.find('0x') != -1):
        imm = int(offset, 16)
    else:
        imm = int(offset)
    if (imm < 0):    # subi
        if (rd == rs1) and (IGNORE_REGS or (rd in REG_LIST)) and \
                (imm > -256) and ('cx.subi8' in ENABLED):
            res = True
            type_code = 'cx.subi8'
        elif (IGNORE_REGS or (rd in REG_LIST and rs1 in REG_LIST)) and \
                (imm > -32) and ('cx.subi5' in ENABLED):
            res = True
            type_code = 'cx.subi5'
    else:   # addi
        if (rd == rs1) and (IGNORE_REGS or (rd in REG_LIST)) and \
                (imm < 256) and ('cx.addi8' in ENABLED):
            res = True
            type_code = 'cx.addi8'
        elif (IGNORE_REGS or (rd in REG_LIST and rs1 in REG_LIST)) and \
                (imm < 32) and ('cx.addi5' in ENABLED):
            res = True
            type_code = 'cx.addi5'
    return (res, (rd, rs1, offset), type_code)


def is_c_addi_replaceable(args, addr):
    """
    Checks if a 16-bit ADDI instruction can be replaced with new ADDI version.

    Returns a tuple of:
        - res: True/False after checking registers and immed size
        - (rd, rs1, immed) of the instruction
        - type_code: 'cx.addi8', 'cx.subi8', ''
    """
    res = False
    type_code = ''
    (rd, rs1, offset) = get_regs_and_offset('c.addi', args)
    if (offset.find('0x') != -1):
        imm = int(offset, 16)
    else:
        imm = int(offset)
    if (imm < 0):    # subi
        if ('cx.subi8' in ENABLED) and (IGNORE_REGS or rd in REG_LIST):
            if (imm > -256):
                res = True
                type_code = 'cx.subi8'
    else:            # addi
        if ('cx.addi5' in ENABLED) and (IGNORE_REGS or rd in REG_LIST):
            if (imm < 256):
                res = True
                type_code = 'cx.addi8'
    return (res, (rd, rs1, offset), type_code)


def is_slli_replaceable(args, addr):
    """
    Checks if a 32-bit SLLI instruction can be replaced with a 16-bit SLLI.

    Returns a tuple of:
        - res: True/False after checking registers and immed size
        - (rd, rs1, immed) of the instruction
        - type_code: 'cx.slli', ''
    """
    res = False
    type_code = ''
    (rd, rs1, offset) = get_regs_and_offset('slli', args)
    if (offset.find('0x') != -1):
        imm = int(offset, 16)
    else:
        imm = int(offset)
    if (IGNORE_REGS or (rd in REG_LIST and rs1 in REG_LIST)) and (imm < 32):
        res = True
        type_code = 'cx.slli'
    return (res, (rd, rs1, offset), type_code)


def is_sw_replaceable(args):
    """
    Checks if a 32-bit SW instruction can be replaced with a 16-bit SW.

    Returns a tuple of:
        - res: True/False after checking registers and offset size
        - (rs2, rs1, offset) of the instruction
        - type_code: 'cx.swzero' (if ENABLED) or ''
    """
    res = False
    type_code = ''
    (rs2, rs1, offset) = get_regs_and_offset('sh', args)
    regs_okay = (rs1 in REG_LIST)
    if (offset.find('0x') != -1):
        offset = int(offset, 16)
    offset_okay = (abs(int(offset)) < 128) and (int(offset) >= 0)
    if (regs_okay) and (rs2 == 'zero') and (offset_okay)\
            and ('cx.swzero' in ENABLED):
        res = True
        type_code = 'cx.swzero'
    return (res, (rs2, rs1, offset), type_code)


def is_j_replaceable(args, comments):
    """
    Checks if a 32-bit J instruction can be replaced with a 16-bit J
    or a 32-bit pop.

    Returns a tuple of:
        - res: True if _restore function being called
        - (rs2, rs1, offset) of the instruction
        - type_code:
            'c.j (restore)' (if ENABLED)
            'pop (restore)' (if ENABLED)
            ''              (otherwise)
    """
    res = False
    type_code = ''
    (rs2, rs1, offset) = get_regs_and_offset('j', args)
    if 'pop (restore)' in ENABLED:
        if (comments is None):
            if (offset.find('_restore') != -1):
                res = True
                type_code = 'pop (restore)'
        elif (comments.find('_restore') != -1):
            res = True
            # pass along the exact function being called
            offset = comments.strip('<>')
            type_code = 'pop (restore)'
    elif 'c.j (restore)' in ENABLED:
        if (comments is None):
            if (offset.find('_restore') != -1):
                res = True
                type_code = 'c.j (restore)'
        elif (comments.find('_restore') != -1):
            res = True
            offset = comments.strip('<>')
            type_code = 'c.j (restore)'

    return (res, (rs2, rs1, offset), type_code)


def is_jal_replaceable(args, comments):
    """
    Checks if a 32-bit JAL instruction can be replaced with a 16-bit JAL
    or a 32-bit push.

    Returns a tuple of:
        - res: True if _save function being called
        - (rs2, rs1, offset) of the instruction
        - type_code:
            'c.jal (save)'  (if ENABLED)
            'push (save)'   (if ENABLED)
            ''              (otherwise)
    """
    res = False
    type_code = ''
    (rs2, rs1, offset) = get_regs_and_offset('jal', args)
    if ('push (save)' in ENABLED):
        if (comments is None):
            if (offset.find('_save') != -1):
                res = True
                type_code = 'push (save)'
        elif (comments.find('_save') != -1):
            res = True
            # pass along the exact function being called
            offset = comments.strip('<>')
            type_code = 'push (save)'
    elif ('c.jal (save)' in ENABLED):
        if (comments is None):
            if (offset.find('_save') != -1):
                res = True
                type_code = 'c.jal (save)'
        elif (comments.find('_save') != -1):
            res = True
            offset = comments.strip('<>')
            type_code = 'c.jal (save)'
    return (res, (rs2, rs1, offset), type_code)


def is_bne_replaceable(args, addr):
    res = False
    type_code = ''
    (rs2, rs1, offset) = get_regs_and_offset('bne', args)
    if ('cx.bne' in ENABLED):
        res = True
        type_code = 'cx.bne'
    return (res, (rs2, rs1, offset), type_code)


def is_blt_replaceable(args, addr):
    res = False
    type_code = ''
    (rs2, rs1, offset) = get_regs_and_offset('blt', args)
    if ('cx.blt' in ENABLED):
        res = True
        type_code = 'cx.blt'
    return (res, (rs2, rs1, offset), type_code)


def is_bge_replaceable(args, addr):
    res = False
    type_code = ''
    (rs2, rs1, offset) = get_regs_and_offset('bge', args)
    if ('cx.bge' in ENABLED):
        res = True
        type_code = 'cx.bge'
    return (res, (rs2, rs1, offset), type_code)


def check_replaceable(opcode, args, comments, curr_max, curr_min, addr):
    """
    Checks if a 32-bit instruction can be replaced with a user instruction.

    Returns a tuple of:
        - res: True/False
        - (r2, r1, offset) of the instruction
        - curr_max: updated max LW offset for the function
        - curr_min: updated min LW offset for the function
        - type_code: new instruction version (if ENABLED)
    """
    res = False
    type_code = ''
    (r2, r1, offset) = (0, 0, 0)
    if (opcode == 'lw') and ('cx.lwpc' in ENABLED):
        res = is_lw_replaceable(args, curr_max, curr_min)
        (res, (r2, r1, offset), curr_max, curr_min) = res
        if (res):
            type_code = 'cx.lwpc'
    if (opcode == 'sb') and ('cx.sb' in ENABLED or 'cx.sbzero' in ENABLED):
        (res, (r2, r1, offset), type_code) = is_sb_replaceable(args)
    if (opcode == 'sh') and ('cx.sh' in ENABLED or 'cx.shzero' in ENABLED):
        (res, (r2, r1, offset), type_code) = is_sh_replaceable(args)
    if (opcode == 'lbu') and ('cx.lbu' in ENABLED):
        (res, (r2, r1, offset), type_code) = is_lbu_replaceable(args)
    if (opcode == 'lhu') and ('cx.lhu' in ENABLED):
        (res, (r2, r1, offset), type_code) = is_lhu_replaceable(args)
    if (opcode == 'lb') and ('cx.lb' in ENABLED):
        (res, (r2, r1, offset), type_code) = is_lb_replaceable(args)
    if (opcode == 'lh') and ('cx.lh' in ENABLED):
        (res, (r2, r1, offset), type_code) = is_lh_replaceable(args)
    if (opcode == 'sw') and ('cx.swzero' in ENABLED):
        (res, (r2, r1, offset), type_code) = is_sw_replaceable(args)
    if (opcode == 'j') and \
            (('c.j (restore)' in ENABLED) or ('pop (restore)' in ENABLED)):
        (res, (r2, r1, offset), type_code) = is_j_replaceable(args, comments)
    if (opcode == 'jal') and \
            (('c.jal (save)' in ENABLED) or ('push (save)' in ENABLED)):
        (res, (r2, r1, offset), type_code) = is_jal_replaceable(args, comments)
    if (opcode == 'bne') and ('cx.bne' in ENABLED):
        (res, (r2, r1, offset), type_code) = is_bne_replaceable(args, addr)
    if (opcode == 'beq') and ('cx.beq' in ENABLED):
        (res, (r2, r1, offset), type_code) = is_beq_replaceable(args, addr)
    if (opcode == 'blt') and ('cx.blt' in ENABLED):
        (res, (r2, r1, offset), type_code) = is_blt_replaceable(args, addr)
    if (opcode == 'bge') and ('cx.bge' in ENABLED):
        (res, (r2, r1, offset), type_code) = is_bge_replaceable(args, addr)
    if (opcode == 'addi'):
        (res, (r2, r1, offset), type_code) = is_addi_replaceable(args, addr)
    if (opcode == 'c.addi'):
        (res, (r2, r1, offset), type_code) = is_c_addi_replaceable(args, addr)
    if (opcode == 'slli') and ('cx.slli' in ENABLED):
        (res, (r2, r1, offset), type_code) = is_slli_replaceable(args, addr)
    return (res, (r2, r1, offset), curr_max, curr_min, type_code)


def check_offsets(func_bytes, reductions, max_offset, min_offset):
    """
    Checks the number of bits required to encode LW offsets for the function.
    Called after a function has been parsed and results are being saved.

    Need num_bits <= 11 to use compressed PC-relative LW instruction.

    Returns a tuple of:
        - res: True/False if number of bits < 11
        - new_min: updated min offset for the function (0 if never updated)
        - num_bits: number of bits to encode offset
    """
    new_min = min_offset
    if (new_min == float("inf")):
        new_min = 0
    # Add up possible reductions to function size
    potential_reductions = 0
    for instr in reductions.keys():
        potential_reductions += reductions[instr]
    # Calculate potential final function + data size (assuming adjacent)
    potential_size = func_bytes - potential_reductions + max_offset - new_min
    # Calculate number of bits to span that size
    num_bits = math.ceil(math.log(potential_size, 2))
    res = (num_bits < 11)
    return (res, new_min, num_bits)
