"""
Excel Summary Worksheet

This file contains functions for creating and modifying the summary worksheet.

Author: Jennifer Hellar

"""

import xlsxwriter
from constants import *
import excel


def create_summary(allflag, rvfile=None, armfile=None):
    """ Creates the basic Summary worksheet. """
    global wksheet
    wksheet = excel.wkbook.add_worksheet('Summary')

    # all benchmarks analysis
    if allflag:
        # Main table
        col_sizes = {0: 8, 1: 40, 2: 20}
        start = len(col_sizes.keys())
        for i in range(start, start+len(BUILDS)):
            col_sizes[i] = 20
        # spacers
        start = len(col_sizes.keys())
        for i in range(start, start+2):
            col_sizes[i] = 15
        # RISC-V final, delta, and minus armcc table
        start = len(col_sizes.keys())
        n_riscv = len([i for i in BUILDS if i.find('rv') != -1])
        for i in range(start, start+n_riscv*3):
            col_sizes[i] = 20
    # single benchmark analysis
    else:
        # Record input files
        wksheet.write('A1', rvfile)
        wksheet.write('A2', armfile)

        # Format column sizes
        col_sizes = {  # Main table
                     0: 8, 1: 40, 2: 20,
                       # RISC-V cols of main table
                     3: 20, 4: 20, 5: 20, 6: 20,
                       # Spacers
                     7: 15, 8: 15,
                       # Compressed Extension Table
                     9: 40, 10: 20, 11: 20, 12: 20, 13: 20, 14: 20,
                       # Chart
                     15: 40, 16: 20,
                       # Compressed Extension Rules Table
                     17: 40, 18: 80}
    for col in col_sizes:
        wksheet.set_column(col, col, col_sizes[col])
    return wksheet


""" Functions to add specific tables/charts to the worksheet """


def add_main_table(row, col, allflag, rvbuild=None, armbuild=None):
    """ Adds the main table ('Function Performance (RISC-V vs. ARM)'). """
    if allflag:
        cols = ['Benchmark'] + BUILDS
    else:
        cols = ['Function (Click to View)',
                armbuild,
                rvbuild,
                # 'IAR',
                rvbuild + ' (final)',
                # 'IAR (Final)',
                rvbuild + ' delta',
                # 'IAR Delta',
                rvbuild + ' (final) - ' + armbuild]
                # 'IAR (Final) - ARM']
    end_row = 200   # To be updated later after data filled in
    end_col = col + len(cols) - 1
    excel.create_table(wksheet, row, col, end_row, end_col,
                       SUMMARY_MAIN_TABLE, cols, False)


def add_totals_table(row, col, allflag, rvbuild=None, armbuild=None):
    """ Adds the totals table ('Benchmark Performance (RISC-V vs. ARM)'). """
    if allflag:
        headers = [''] + BUILDS
        row_labels = ['Totals (bytes)',
                      '% of ' + armbuild,
                      '% of ' + rvbuild]
    else:
        headers = ['',
                   armbuild,
                   rvbuild,
                   rvbuild + ' (final)',
                   rvbuild + ' delta',
                   rvbuild + ' (final) - ' + armbuild]
        row_labels = ['Totals (bytes)',
                      '% of ' + armbuild,
                      '% of ' + rvbuild]

    end_row = row + len(row_labels) + 2
    end_col = col + len(headers) - 1
    # Create table and add row labels
    excel.create_table(wksheet, row, col, end_row, end_col,
                       SUMMARY_TOTALS_TABLE, headers, True)
    excel.add_row_labels(wksheet, SUMMARY_TOTALS_TABLE, row_labels)

    if allflag:
        for build in BUILDS:
            table = SUMMARY_TOTALS_TABLE
            # Add formulas for the Totals row
            cell = excel.get_table_cell(table, build, 'Totals (bytes)')
            excel.sum_col(wksheet, SUMMARY_MAIN_TABLE, build, cell)
            # Add formulas for the % of armcc row
            denom_cell = excel.get_table_cell(table, armbuild, 'Totals (bytes)')
            num_cell = excel.get_table_cell(table, build, 'Totals (bytes)')
            dest_cell = excel.get_table_cell(table, build, '% of '+armbuild)
            excel.record_percentage(wksheet, num_cell, denom_cell, dest_cell, 1, False)
            # Add formulas for the % of rvgcc row
            denom_cell = excel.get_table_cell(table, rvbuild, 'Totals (bytes)')
            num_cell = excel.get_table_cell(table, build, 'Totals (bytes)')
            dest_cell = excel.get_table_cell(table, build, '% of '+rvbuild)
            excel.record_percentage(wksheet, num_cell, denom_cell, dest_cell, 1, False)
    else:
        # Add formulas for the Totals row
        cell = excel.get_table_cell(SUMMARY_TOTALS_TABLE, armbuild, row_labels[0])
        excel.sum_col(wksheet, SUMMARY_MAIN_TABLE, armbuild, cell)
        cell = excel.get_table_cell(SUMMARY_TOTALS_TABLE, rvbuild, row_labels[0])
        excel.sum_col(wksheet, SUMMARY_MAIN_TABLE, rvbuild, cell)

        colname = headers[3]
        cell = excel.get_table_cell(SUMMARY_TOTALS_TABLE, colname, row_labels[0])
        excel.sum_col(wksheet, SUMMARY_MAIN_TABLE, colname, cell)

        colname = headers[4]
        cell = excel.get_table_cell(SUMMARY_TOTALS_TABLE, colname, row_labels[0])
        excel.sum_col(wksheet, SUMMARY_MAIN_TABLE, colname, cell)
        # Conditional format RVGCC Delta total to be red/green if >/< 0
        wksheet.conditional_format(cell, {'type': 'cell', 'criteria': '>',
                                          'value': 0,
                                          'format': excel.red_light_format})
        wksheet.conditional_format(cell, {'type': 'cell', 'criteria': '<',
                                          'value': 0,
                                          'format': excel.green_light_format})

        # Conditional format RVGCC (Final) - ARM total to be red/green if >/< 0
        colname = headers[5]
        cell = excel.get_table_cell(SUMMARY_TOTALS_TABLE, colname, row_labels[0])
        excel.sum_col(wksheet, SUMMARY_MAIN_TABLE, colname, cell)
        wksheet.conditional_format(cell, {'type': 'cell', 'criteria': '>',
                                          'value': 0,
                                          'format': excel.red_light_format})
        wksheet.conditional_format(cell, {'type': 'cell', 'criteria': '<',
                                          'value': 0,
                                          'format': excel.green_light_format})

        # Add formulas for the % of ARM row
        denom_cell = excel.get_table_cell(SUMMARY_TOTALS_TABLE, armbuild,
                                          row_labels[0])
        table = SUMMARY_TOTALS_TABLE
        num_cell = excel.get_table_cell(table, headers[1], row_labels[0])
        dest_cell = excel.get_table_cell(table, headers[1], row_labels[1])
        excel.record_percentage(wksheet, num_cell, denom_cell, dest_cell, 1, False)

        num_cell = excel.get_table_cell(table, headers[2], row_labels[0])
        dest_cell = excel.get_table_cell(table, headers[2], row_labels[1])
        excel.record_percentage(wksheet, num_cell, denom_cell, dest_cell, 1, False)

        num_cell = excel.get_table_cell(table, headers[3], row_labels[0])
        dest_cell = excel.get_table_cell(table, headers[3], row_labels[1])
        excel.record_percentage(wksheet, num_cell, denom_cell, dest_cell, 1, False)

        num_cell = excel.get_table_cell(table, headers[5], row_labels[0])
        dest_cell = excel.get_table_cell(table, headers[5], row_labels[1])
        # Threshold is 0 because this is relative number
        excel.record_percentage(wksheet, num_cell, denom_cell, dest_cell, 0, False)

        denom_cell = excel.get_table_cell(table, headers[2], row_labels[0])
        num_cell = excel.get_table_cell(table, headers[4], row_labels[0])
        dest_cell = excel.get_table_cell(table, headers[4], row_labels[2])
        excel.record_percentage(wksheet, num_cell, denom_cell, dest_cell, 1, False)


def add_replaced_instr_table(reductions, rvbuild, armbuild):
    """
    Adds a table listing the compact instruction reductions.

    Location: same row as Totals table,
        3 columns over from Totals/Main table (whichever is wider)

    """
    # Set the table location and column headers
    coord = excel.get_table_loc(SUMMARY_TOTALS_TABLE)
    table_row = coord[0]
    table_col = max(coord[3], excel.get_table_loc(SUMMARY_MAIN_TABLE)[3]) + 3
    headers = ['Instruction',
               rvbuild + ' reduction',
               rvbuild + ' percentage']
    end_row = 200
    end_col = table_col + len(headers) - 1
    excel.create_table(wksheet, table_row, table_col, end_row, end_col,
                       SUMMARY_INSTR_TABLE, headers, False)

    names = []
    vals = []
    for nm in reductions.keys():
        names.append(nm)
        vals.append(reductions[nm])

    # Start of data
    row = table_row + 3
    # Divide by total to get percentage reduction
    denom = excel.get_table_cell(SUMMARY_TOTALS_TABLE, rvbuild, 'Totals (bytes)')
    table = SUMMARY_INSTR_TABLE
    for i in range(len(names)):
        # Vertical labels are instruction names
        col = excel.get_table_col(table, 'Instruction')
        wksheet.write_string(row, col, names[i], excel.header_format)

        # Update the table map to include the reduction and percentage cells
        excel.update_table_map(table, headers[1], names[i], row)
        excel.update_table_map(table, headers[2], names[i], row)

        # Record the reduction values
        col = excel.get_table_col(table, headers[1])
        wksheet.write_number(row, col, vals[i], excel.light_bg_format)

        # Record the percentages (green if > 0)
        num = excel.get_table_cell(table, headers[1], names[i])
        dest = excel.get_table_cell(table, headers[2], names[i])
        excel.record_percentage(wksheet, num, denom, dest, 0, True)

        row += 1

    # Save the location/size of the table
    excel.update_table_loc(SUMMARY_INSTR_TABLE, table_row, table_col,
                           row - 1, end_col)


def add_replaced_instr_chart(build):
    """ Add chart to visualize compact instruction reductions. """
    # Location of data table
    coord = excel.get_table_loc(SUMMARY_INSTR_TABLE)
    # Location of chart (to the right of data table)
    row = coord[0]
    col = coord[3] + 2
    chart_loc = CELL_NAME[(row, col)]
    chart = excel.wkbook.add_chart({'type': 'column'})
    # Location of instruction names
    name_col = excel.get_table_col(SUMMARY_INSTR_TABLE, 'Instruction')
    start_nm_cell = CELL_NAME[(coord[0] + 3, name_col)]
    end_nm_cell = CELL_NAME[(coord[2], name_col)]
    # Location of reduction percentage values
    val_col_name = build + ' percentage'
    val_col = excel.get_table_col(SUMMARY_INSTR_TABLE, val_col_name)
    start_val_cell = CELL_NAME[(coord[0] + 3, val_col)]
    end_val_cell = CELL_NAME[(coord[2], val_col)]
    chart.add_series({
        'name':         build,
        'categories':   '=Summary!' + start_nm_cell + ':' + end_nm_cell,
        'values':       '=Summary!' + start_val_cell + ':' + end_val_cell,
        })
    chart.set_title({'name': 'Compressed Extension Reductions'})
    chart.set_style(10)
    chart.set_size({'width': 500, 'height': 340})
    wksheet.insert_chart(chart_loc, chart, {'x_offset': 0, 'y_offset': 0})


def add_replacement_rules_table():
    """
    description
    """
    # Set the table location and column headers
    coord = excel.get_table_loc(SUMMARY_INSTR_TABLE)
    table_row = coord[0]
    table_col = coord[3] + 6
    table = SUMMARY_RULES_TABLE
    headers = ['Replaced Instruction',
               'Rules']
    end_row = table_row + len(ENABLED) + 2
    end_col = table_col + len(headers) - 1
    excel.create_table(wksheet, table_row, table_col, end_row, end_col,
                       table, headers, False)
    row = table_row + 3
    for instr in ENABLED:
        # Rules applied
        if (instr == 'cx.lwpc'):
            rule_text = '32-bit lw; rs1 = gp; ' + \
                '# Bits to address func + data <= 8; rd in ' + str(REG_LIST)
        elif (instr == 'c.j (restore)') or (instr == 'pop (restore)'):
            rule_text = '32-bit J; __riscv_restore destination'
        elif (instr == 'c.jal (save)') or (instr == 'push (save)'):
            rule_text = '32-bit JAL; __riscv_save destination'
        elif (instr[:4] == 'cx.b'):
            rule_text = '32-bit Branch; 90% replacement'
        elif (instr[:-3] == 'cx.addi'):
            rule_text = '32- or 16-bit ADDI; '
            if (instr[-2:] == 'u8'):
                rule_text = rule_text + '0 <= imm < 256; rd = rs1 in ' + \
                    str(REG_LIST)
            else:
                rule_text = rule_text + '0 <= imm < 32; rs1, rd in ' + \
                    str(REG_LIST)
        elif (instr[:-3] == 'cx.subi'):
            rule_text = '32- or 16-bit ADDI; '
            if (instr[-2:] == 'u8'):
                rule_text = rule_text + '-256 < imm < 0; rd = rs1 in ' + \
                    str(REG_LIST)
            else:
                rule_text = rule_text + '-32 <= imm < 0; rs1, rd in ' + \
                    str(REG_LIST)
        elif (instr == 'cx.slli'):
            rule_text = '32-bit slli; rs1, rd in ' + str(REG_LIST)
        else:
            rule_text = '32-bit ' + instr[3:6] + '; 0 <= offset < 128'
            if (instr == 'cx.sb') or (instr == 'cx.sh'):
                rule_text = rule_text + '; rs1, rs2 in ' + str(REG_LIST)
            elif (instr == 'cx.lbu') or (instr == 'cx.lhu') or \
                    (instr == 'cx.lb') or (instr == 'cx.lh'):
                rule_text = rule_text + '; rs1, rd in ' + str(REG_LIST)
            if (instr == 'cx.sbzero') or (instr == 'cx.shzero') \
                    or (instr == 'cx.swzero'):
                rule_text = rule_text + '; rs2 = zero; rs1 in ' + str(REG_LIST)
        # Vertical labels are instruction names
        col = excel.get_table_col(table, 'Replaced Instruction')
        wksheet.write_string(row, col, instr, excel.header_format)
        # Update the table map to include the rules cell
        excel.update_table_map(table, 'Rules', instr, row)
        # Record the rules
        col = excel.get_table_col(table, 'Rules')
        wksheet.write_string(row, col, rule_text, excel.light_bg_format)
        row += 1

    # Save the location/size of the table
    excel.update_table_loc(SUMMARY_RULES_TABLE, table_row, table_col,
                           row - 1, end_col)


def add_instr_formats_tables(formats, build):
    """ Add the Instruction Format tables to the 'tmp' worksheet. """
    # Location: tmp worksheet
    sheet = excel.wkbook.get_worksheet_by_name('tmp')
    row = 0
    col = 3
    headers = ['Instruction', '# (' + build + ')']
    # rows are base instructions
    tables = []
    row_labels = []
    for lbl in formats.keys():
        tables.append(lbl + ' (Total)')
        for instr in formats[lbl]:
            row_labels.append(instr)

    end_row = row + len(row_labels) + 2
    # create the tables
    for table in tables:
        end_col = col + len(headers) - 1
        excel.create_table(sheet, row, col, end_row, end_col,
                           table, headers, False)
        excel.add_row_labels(sheet, table, row_labels)
        col = col + len(headers)
    # Write the data to the corresponding table
    for lbl in formats.keys():
        table_nm = lbl + ' (Total)'
        c_formats = formats[lbl]
        for instr in c_formats:
            val = c_formats[instr]
            cell = excel.get_table_cell(table_nm, '# (' + build + ')', instr)
            sheet.write_number(cell, val, excel.light_bg_format)


def add_instr_formats_radar(compiler):
    """ Add radar to visualize most frequent instruction formats. """
    # Location of chart: below instruction frequency table
    coord = excel.get_table_loc(SUMMARY_INSTR_TABLE)
    ch_row = max(coord[2] + 8, coord[0] + 19)
    if (compiler == 'rvgcc'):
        ch_col = coord[1]
    chart_loc_cell = CELL_NAME[(ch_row, ch_col)]

    # Make the pie chart underneath to mark the instruction format
    chart = excel.wkbook.add_chart({'type': 'pie'})
    chart.add_series({
        'categories':   ['tmp', 0, 0, len(RV32_FORMATS) - 1, 0],
        'values':       ['tmp', 0, 1, len(RV32_FORMATS) - 1, 1],
        })
    # Chart title
    chart.set_title({'name': compiler + ' instruction formats',
                     'layout': {'x': 0.01, 'y': 0.01}})
    chart.set_legend({'position': 'overlay_right'})
    chart.set_size({'width': 730, 'height': 590})
    chart.set_chartarea({'border': {'none': True}})
    chart.set_plotarea({'border': {'none': True}})
    chart.set_rotation(357)
    wksheet.insert_chart(chart_loc_cell, chart)

    # Make the radar chart
    chart = excel.wkbook.add_chart({'type': 'radar'})
    # Data is located on the 'tmp' worksheet
    tmp_sheet = excel.wkbook.get_worksheet_by_name('tmp')
    for i in range(len(RV32_FORMATS)):
        lbl = RV32_FORMATS[i]
        (row, col, end_row, end_col) = excel.get_table_loc(lbl + ' (Total)')
        name = [tmp_sheet.get_name(), row, col]
        categories = [tmp_sheet.get_name(), row + 3, col, end_row, col]
        val_col = excel.get_table_col(lbl + ' (Total)', '# (' + compiler + ')')
        values = [tmp_sheet.get_name(), row + 3, val_col, end_row, val_col]
        chart.add_series({
                'name':         name,
                'categories':   categories,
                'values':       values,
                'line':         {'color': 'black'},
                'marker':       {'type': 'diamond', 'fill': {'color': 'black'},
                                 'border': {'color': 'black'}, 'size': 8}
            })
    chart.set_size({'width': 730, 'height': 590})
    chart.set_chartarea({'fill': {'none': True}, 'border': {'none': True}})
    chart.set_plotarea({'fill': {'none': True}})
    chart.set_legend({'none': True})
    ch_row = ch_row + 1
    chart_loc_cell = CELL_NAME[(ch_row, ch_col)]
    wksheet.insert_chart(chart_loc_cell, chart, {'x_offset': 0, 'y_offset': 0})


def add_total_instr_table(total, keep, compiler):
    """ Add a table to list the most common instructions. """
    vals = []
    names = []
    for instr in total.keys():
        # Mark instruction names based on size
        freq = total[instr]
        names.append(instr)
        vals.append(freq)
    # Combine the lists and sort the tuples by the value
    vlnm = sorted(zip(vals, names))
    # Separate the (sorted) lists again
    vals = [val for val, nm in vlnm]
    names = [nm for val, nm in vlnm]

    # Display most common pairs individually, the rest in 'other' category
    other = sum(vals[:-keep])
    vals = vals[-keep:]
    names = names[-keep:]
    vals.reverse()
    names.reverse()
    vals.append(other)
    names.append('other')

    # Location for the table and headers
    coord = excel.get_table_loc(SUMMARY_INSTR_TABLE)
    row = max(coord[2] + 44, coord[0] + 57)
    if (compiler == 'rvgcc'):
        col = coord[1]
        table = SUMMARY_RVGCC_INSTR_TOT_TABLE
    headers = ['instruction',
               '# of occurrences',
               'percentage']
    end_row = row + len(names) + 3  # extra row for totals
    end_col = col + len(headers) - 1
    excel.create_table(wksheet, row, col, end_row, end_col,
                       table, headers, True)

    # Location of data start
    row += 3
    start_name = CELL_NAME[(row, col)]
    start_val = CELL_NAME[(row, col + 1)]
    start_perc = CELL_NAME[(row, col + 2)]
    for i in range(len(vals)):
        instr = names[i]
        # Mark 'cx' instructions with gold text
        if (instr in ENABLED):
            name_format = excel.gold_header_format
            val_format = excel.light_bg_format
        # Mark 32-bit instructions with red text
        elif (instr.find('c.') == -1) and (instr != 'other'):
            name_format = excel.red_header_format
            val_format = excel.red_light_format
        # Mark 16-bit instructions that need to be replaced
        elif (instr == 'c.addi') and (addi_subi_en):
            name_format = excel.orange_header_format
            val_format = excel.orange_light_format
        else:
            name_format = excel.header_format
            val_format = excel.light_bg_format
        # Write the pair name
        name_cell = CELL_NAME[(row + i, col)]
        wksheet.write_string(name_cell, instr, name_format)
        # Write the number of occurences
        val_cell = CELL_NAME[(row + i, col + 1)]
        wksheet.write_number(val_cell, vals[i], val_format)
        # Update the table mapping to include these cells
        excel.update_table_map(table, 'instruction', instr, row + i)
        excel.update_table_map(table, '# of occurrences', instr, row + i)
        excel.update_table_map(table, 'percentage', instr, row + i)

    end_val = val_cell
    # Add a total formula at the bottom of the table
    formula = '=SUM(' + start_val + ':' + end_val + ')'
    total_cell = CELL_NAME[(row + len(vals), col + 1)]
    wksheet.write_formula(total_cell, formula, excel.bold_light_format)
    row = row + len(vals)
    wksheet.write_string(row, col, 'Total:', excel.bold_light_format)
    # Add the percentage formula to the appropriate column
    end_perc = CELL_NAME[(row - 2, col + 2)]
    formula = '=(' + start_val + ':' + end_val + ')/' + total_cell
    wksheet.write_array_formula(start_perc + ':' + end_perc, formula,
                                excel.percent_format)


def add_pairs_table(pairs, keep, compiler, armbuild):
    """ Add a table to list the most common instruction pairs. """
    vals = []
    names = []
    for pair in pairs.keys():
        vals.append(pairs[pair])
        names.append(pair)
    # Combine the lists and sort the tuples by the value
    vlnm = sorted(zip(vals, names))
    # Separate the (sorted) lists again
    vals = [val for val, nm in vlnm]
    names = [nm for val, nm in vlnm]

    # Display most common pairs individually, the rest in 'other' category
    other = sum(vals[:-keep])
    vals = vals[-keep:]
    names = names[-keep:]
    vals.reverse()
    names.reverse()
    vals.append(other)
    names.append('other')

    # Location for the table and headers
    row = excel.get_table_loc(SUMMARY_RVGCC_INSTR_TOT_TABLE)[2] + 8
    if (compiler == 'rvgcc'):
        col = excel.get_table_loc(SUMMARY_INSTR_TABLE)[1]
        table = SUMMARY_RVGCC_PAIRS_TABLE
    headers = ['Instruction Pair',
               '# of Occurrences',
               'Reduction (Rel. to ARM)']
    end_row = row + len(names) + 3  # extra row for totals
    end_col = col + len(headers) - 1
    excel.create_table(wksheet, row, col, end_row, end_col,
                       table, headers, True)

    # Location of data start
    row += 3
    start_name = CELL_NAME[(row, col)]
    start_val = CELL_NAME[(row, col + 1)]
    start_perc = CELL_NAME[(row, col + 2)]
    denom = excel.get_table_cell(SUMMARY_TOTALS_TABLE, armbuild,
                                 'Totals (bytes)')
    for i in range(len(vals)):
        # Write the pair name
        name_cell = CELL_NAME[(row + i, col)]
        if names[i] != 'other':
            (prev, curr) = names[i]
            # nm = prev + ' -> ' + curr
            nm = '{:<15}{:<15}{:<15}'.format(prev, '->', curr)
        else:
            nm = names[i]
        wksheet.write_string(name_cell, nm, excel.header_format)
        # Write the number of occurences
        val_cell = CELL_NAME[(row + i, col + 1)]
        wksheet.write_number(val_cell, vals[i], excel.light_bg_format)
        if names[i] != 'other':
            # Write the potential percentage reduction
            perc_cell = CELL_NAME[(row + i, col + 2)]
            if (prev.find('c.') != -1) and (curr.find('c.') != -1):
                b = '2'  # 2 bytes saved if combined to 1 16-bit instruction
            elif (prev.find('c.') == -1) and (curr.find('c.') == -1):
                b = '4'  # 4 bytes saved if combined to 1 32-bit instruction
            else:
                b = '2'  # 2 bytes saved if combined to 1 32-bit instruction
            formula = '= -' + b + '*(' + val_cell + '/' + denom + ')'
            wksheet.write_formula(perc_cell, formula, excel.percent_format)
        # Update the table mapping to include these cells
        excel.update_table_map(table, 'Instruction Pair', nm, row + i)
        excel.update_table_map(table, '# of Occurrences', nm, row + i)
        excel.update_table_map(table, 'Reduction (Rel. to ARM)',
                               nm, row + i)

    end_val = val_cell
    # Add a total formula at the bottom of the table
    formula = '=SUM(' + start_val + ':' + end_val + ')'
    total_cell = CELL_NAME[(row + len(vals), col + 1)]
    wksheet.write_formula(total_cell, formula, excel.bold_light_format)
    row = row + len(vals)
    wksheet.write_string(row, col, 'Total:', excel.bold_light_format)


def add_overshoot_table(results, arm_results, keep, compiler):
    """ Add a table to list the functions which overshoot ARM by the most. """
    # Create lists of overshoots and corresponding function names
    vals = []
    names = []
    for name in results.keys():
        if (name != '__riscv_save') and (name != '__riscv_restore'):
            # Total the reduction for each function
            reductions_dict = results[name][1]
            total_red = 0
            for instr in reductions_dict.keys():
                total_red += reductions_dict[instr]
            # Calculate the overshoot remaining after reduction
            diff = results[name][0] - total_red - arm_results[name]
            vals.append(diff)
            names.append(name)
    # Combine the lists and sort the tuples by the value
    vlnm = sorted(zip(vals, names))
    # Ignore functions which are not greater than ARM
    vlnm = [(val, nm) for val, nm in vlnm if val > 0]
    # Separate the (sorted) lists again
    vals = [val for val, nm in vlnm]
    names = [nm for val, nm in vlnm]

    # Display some functions individually, the rest in 'other' category
    other = sum(vals[:-keep])
    vals = vals[-keep:]
    names = names[-keep:]
    vals.reverse()
    names.reverse()
    vals.append(other)
    names.append('other')

    # Location for the table and headers
    if (compiler == 'rvgcc'):
        coord = excel.get_table_loc(SUMMARY_RVGCC_PAIRS_TABLE)
        table = SUMMARY_RVGCC_OVERSHOOT_TABLE
    row = coord[2] + 8
    col = coord[1]
    headers = ['Function (Click to View)',
               'Overshoot (bytes)',
               '% of Total']
    end_row = row + len(names) + 3  # extra row for total
    end_col = col + len(headers) - 1
    excel.create_table(wksheet, row, col, end_row, end_col,
                       table, headers, True)

    # Location of data start
    row += 3
    start_name_cell = CELL_NAME[(row, col)]
    start_val_cell = CELL_NAME[(row, col + 1)]
    start_perc_cell = CELL_NAME[(row, col + 2)]

    for i in range(len(vals)):
        name_cell = CELL_NAME[(row + i, col)]   # cell for the function name
        nm = names[i]                           # actual function name
        # Write the function name (with a link to its worksheet)
        if nm != 'other':
            formula = '=HYPERLINK("#' + nm[11:] + '!A1", "' + nm + '")'
            wksheet.write_formula(name_cell, formula, excel.header_format)
        else:
            wksheet.write_string(name_cell, nm, excel.header_format)
        # Write the function overshoot value
        val_cell = CELL_NAME[(row + i, col + 1)]
        wksheet.write_number(val_cell, vals[i], excel.light_bg_format)
        # Update the table mapping to include these cells
        excel.update_table_map(table, 'Function (Click to View)', nm, row + i)
        excel.update_table_map(table, 'Overshoot (bytes)', nm, row + i)
        excel.update_table_map(table, '% of Total', nm, row + i)

    end_name_cell = name_cell
    end_val_cell = val_cell
    end_perc_cell = excel.get_table_cell(table, '% of Total',
                                         'other')
    # Add a total overshoot formula at the bottom of the table
    formula = '=SUM(' + start_val_cell + ':' + end_val_cell + ')'
    total_cell = CELL_NAME[(row + len(vals), col + 1)]
    wksheet.write_formula(total_cell, formula, excel.bold_light_format)
    wksheet.write_string(row + len(vals), col, 'Total:',
                         excel.bold_light_format)
    # Add the percentage formula to the appropriate column
    formula = '=(' + start_val_cell + ':' + end_val_cell + ')/' + total_cell
    wksheet.write_array_formula(start_perc_cell + ':' + end_perc_cell, formula,
                                excel.percent_format)


def add_overshoot_chart(compiler):
    """ Adds a chart of the function overshoots (table must exist first). """
    # Location of the data table
    if (compiler == 'rvgcc'):
        table = SUMMARY_RVGCC_OVERSHOOT_TABLE
    coord = excel.get_table_loc(table)
    # Location of function names
    col = excel.get_table_col(table, 'Function (Click to View)')
    start_name_cell = CELL_NAME[(coord[0] + 3, col)]
    end_name_cell = excel.get_table_cell(table, 'Function (Click to View)',
                                         'other')
    # Location of overshoot values
    col = excel.get_table_col(table, 'Overshoot (bytes)')
    start_val_cell = CELL_NAME[(coord[0] + 3, col)]
    end_val_cell = excel.get_table_cell(table, 'Overshoot (bytes)', 'other')
    # Location of the chart
    row = coord[2] + 8
    col = coord[1]
    chart_loc = CELL_NAME[(row, col)]
    chart1 = excel.wkbook.add_chart({'type': 'pie'})
    chart1.add_series({
        'name':         'Function Contribution to Overshoot Data',
        'categories':   '=Summary!' + start_name_cell + ':' + end_name_cell,
        'values':       '=Summary!' + start_val_cell + ':' + end_val_cell,
        'data_labels':  {'percentage': True, 'position': 'outside_end'}
        })
    chart1.set_title({'name':
                      compiler + ' Overshoot (by Function)'})
    chart1.set_style(10)
    chart1.set_size({'width': 650, 'height': 320})
    wksheet.insert_chart(chart_loc, chart1, {'x_offset': 0, 'y_offset': 0})


""" Functions to record data to the worksheet """


def record_all_main(results, benchmarks):
    table = SUMMARY_MAIN_TABLE
    coord = excel.get_table_loc(SUMMARY_MAIN_TABLE)
    (table_row, table_col, table_end_row, table_end_col) = coord
    row = table_row + 3     # Start of data rows
    # Number the functions
    wksheet.write_column(row, 0, [i for i in range(len(benchmarks))])
    curr_format = excel.light_bg_format
    for b in benchmarks:
        # Benchmark name
        col = excel.get_table_col(table, 'Benchmark')
        wksheet.write_string(row, col, b, curr_format)

        # Benchmark sizes
        for build in results.keys():
            if build.find('arm') != -1:
                size = results[build][b]
            elif build.find('rv') != -1:
                size = results[build][b][0]
            col = excel.get_table_col(table, build)
            wksheet.write_number(row, col, size, curr_format)

        row += 1
        # Alternate background colors
        if curr_format == excel.light_bg_format:
            curr_format = excel.dark_bg_format
        else:
            curr_format = excel.light_bg_format

    # Save the location of the table
    excel.update_table_loc(table, table_row, table_col, row - 1, table_end_col)


def record_riscv_data(func, total_reductions, rvbuild):
    """
    Records the RISC-V results for all benchmark functions to the main table.

    Fills in and formats the following columns:
        - Function (Click to View)      - RVGCC
        - RVGCC (Final)               - # Bits to Encode Offset
        - 'RVGCC Delta'

    """
    table = SUMMARY_MAIN_TABLE
    coord = excel.get_table_loc(SUMMARY_MAIN_TABLE)
    (table_row, table_col, table_end_row, table_end_col) = coord
    row = table_row + 3     # Start of data rows
    # Number the functions
    wksheet.write_column(row, 0, [i for i in range(len(func.keys()))])
    curr_format = excel.light_bg_format
    # Record the values for each function
    for nm in func.keys():
        if (nm != '__riscv_save') and (nm != '__riscv_restore'):
            (total, reductions, instr_freq, instr_types, bits) = func[nm]
            # Calculate the total reduction for the function
            func_reduction = 0
            for instr in reductions.keys():
                func_reduction += reductions[instr]
            # Function name (with link to appropriate worksheet)
            sheet = nm
            formula = '=HYPERLINK("#' + sheet + '!A1", "' + nm + '")'
            col = excel.get_table_col(table, 'Function (Click to View)')
            wksheet.write_formula(row, col, formula, curr_format)
            # 'RVGCC'
            col = excel.get_table_col(table, rvbuild)
            wksheet.write_number(row, col, total, curr_format)
            # 'RVGCC (Final)'
            reduced = total - func_reduction
            col = excel.get_table_col(table, rvbuild + ' (final)')
            wksheet.write_number(row, col, reduced, curr_format)
            row += 1
            # Alternate background colors
            if curr_format == excel.light_bg_format:
                curr_format = excel.dark_bg_format
            else:
                curr_format = excel.light_bg_format
    if (save_restore_en):
        # '__riscv_save' and '__riscv_restore' go last
        (total, r, i, t, b) = func['__riscv_save']
        sheet = '__riscv_save'
        formula = '=HYPERLINK("#' + sheet + '!A1", "' + '__riscv_save' + '")'
        col = excel.get_table_col(table, 'Function (Click to View)')
        wksheet.write_formula(row, col, formula, curr_format)
        # 'RVGCC'
        col = excel.get_table_col(table, rvbuild)
        wksheet.write_number(row, col, total, curr_format)
        # 'RVGCC (Final)'
        col = excel.get_table_col(table, rvbuild + ' (final)')
        if ('push (save)' in ENABLED):
            wksheet.write_number(row, col, 0, curr_format)
        else:
            wksheet.write_number(row, col, total, curr_format)
        row += 1
        # Alternate backgrounds
        if curr_format == excel.light_bg_format:
            curr_format = excel.dark_bg_format
        else:
            curr_format = excel.light_bg_format
        # '__riscv_restore'
        (total, r, i, t, b) = func['__riscv_restore']
        sheet = '__riscv_restore'
        formula = '=HYPERLINK("#' + sheet + '!A1", "' + '__riscv_restore' + '")'
        col = excel.get_table_col(table, 'Function (Click to View)')
        wksheet.write_formula(row, col, formula, curr_format)
        # 'RVGCC'
        col = excel.get_table_col(table, rvbuild)
        wksheet.write_number(row, col, total, curr_format)
        # 'RVGCC (Final)'
        col = excel.get_table_col(table, rvbuild + ' (final)')
        if ('pop (restore)' in ENABLED):
            wksheet.write_number(row, col, 0, curr_format)
        else:
            wksheet.write_number(row, col, total, curr_format)
        row += 1

    # Save the location of the table
    excel.update_table_loc(table, table_row, table_col, row - 1, table_end_col)
    # Calculate 'RVGCC Delta'
    excel.subtract_col(wksheet, table, rvbuild + ' (final)', rvbuild,
                       rvbuild + ' delta')


def record_arm_data(rv_results, arm_results, rvbuild, armbuild):
    """
    Records the ARM results for all benchmark functions to the main table.

    Fills in and formats the following columns:
        - 'ARM'         - 'RISC-V (Final) - ARM'
    """
    coord = excel.get_table_loc(SUMMARY_MAIN_TABLE)
    (table_row, table_col, table_end_row, table_end_col) = coord
    row = table_row + 3
    curr_format = excel.light_bg_format
    for func_name in rv_results.keys():
        if (func_name != '__riscv_save') and (func_name != '__riscv_restore'):
            bytes = arm_results[func_name]
            col = excel.get_table_col(SUMMARY_MAIN_TABLE, armbuild)
            wksheet.write_number(row, col, bytes, curr_format)
            row += 1
            # Alternate backgrounds for each row
            if curr_format == excel.light_bg_format:
                curr_format = excel.dark_bg_format
            else:
                curr_format = excel.light_bg_format
    # Calculate 'RVGCC (Final) - ARM'
    excel.subtract_col(wksheet, SUMMARY_MAIN_TABLE, rvbuild + ' (final)',
                       armbuild, rvbuild + ' (final) - ' + armbuild)
