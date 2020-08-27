import os

import xlsxwriter
from flask import current_app, safe_join
from flask_login import current_user

from citywok_manager.models import Employee


def get_pk(obj):
    return str(obj)


def employee2excel():
    # delete the old file
    path = safe_join(current_app.root_path,
                     'download/employee/employee_info.xlsx')
    if os.path.isfile(path):
        os.unlink(path)

    # create new workbook
    wb = xlsxwriter.Workbook(path)

    # worksheet of all employee information
    ws = wb.add_worksheet('员工档案')

    # format of heads and cells
    heads_format = wb.add_format({'font_name': 'Microsoft YaHei',
                                  'bold': True,
                                  'align': 'left',
                                  'font_size': 12,
                                  'border': 1})
    cells_format = wb.add_format({'font_name': 'Microsoft YaHei',
                                  'align': 'left'})
    date_format = wb.add_format({'font_name': 'Microsoft YaHei',
                                 'align': 'left',
                                 'num_format': 'yyyy-mm-dd'})
    money_format = wb.add_format({'font_name': 'Microsoft YaHei',
                                  'align': 'left',
                                  'num_format': '#,##0.00 [$€-x-euro1]'})

    # create and add data to the table
    heads = list(Employee.get_heads().values())
    employees = Employee.query.filter_by(is_active=True).all()
    spec = [{'header': x,
             'header_format': heads_format} for x in heads]
    data = [list(employee.get_data().values()) for employee in employees]

    ws.add_table(0, 0, len(employees), len(heads) - 1,
                 {'data': data, 'style': 'Table Style Medium 15', 'columns': spec})

    # data format
    for i in range(len(heads)):
        if i in (5, 15):
            ws.set_column(i, i, 11, date_format)
        elif i in(16, 17):
            ws.set_column(i, i, None, money_format)
        else:
            ws.set_column(i, i, None, cells_format)
    # setting for print
    print_setting(ws, '&C&"Microsoft YaHei,Bold"&20员工档案')

    # worksheet of all employee information
    ws = wb.add_worksheet('离职员工')

    # create and add data to the table
    heads = list(Employee.get_heads().values())
    employees = Employee.query.filter_by(is_active=False).all()
    spec = [{'header': x,
             'header_format': heads_format} for x in heads]
    data = [list(employee.get_data().values()) for employee in employees]
    ws.add_table(0, 0, len(employees), len(heads) - 1,
                 {'data': data, 'style': 'Table Style Medium 15', 'columns': spec})
    # data format
    for i in range(len(heads)):
        if i in (5, 15):
            ws.set_column(i, i, 11, date_format)
        elif i in(16, 17):
            ws.set_column(i, i, None, money_format)
        else:
            ws.set_column(i, i, None, cells_format)
    # setting for print
    print_setting(ws, '&C&"Microsoft YaHei,Bold"&20离职员工')

    heads_format = wb.add_format({'font_name': 'Microsoft YaHei',
                                  'bold': True,
                                  'align': 'left',
                                  'font_size': 18,
                                  'border': 1})
    cells_format = wb.add_format({'font_name': 'Microsoft YaHei',
                                  'font_size': 16,
                                  'align': 'left',
                                  'valign': 'vcenter'})
    ws = wb.add_worksheet('名单')
    keys = ('id', 'first_name', 'last_name', 'zh_name')
    heads = [Employee.get_heads()[key] for key in keys]
    heads.append(None)
    employees = Employee.query.filter_by(is_active=True).all()
    spec = [{'header': x,
             'header_format': heads_format} for x in heads]
    data = []
    for employee in employees:
        data.append([employee.get_data()[key] for key in keys])
    ws.add_table(0, 0, len(employees), len(heads) - 1,
                 {'data': data, 'style': 'Table Style Medium 15', 'columns': spec})

    for i in range(len(employees)):
        ws.set_row(i + 1, 30, cells_format)

    print_setting(ws, '&C&"Microsoft YaHei,Bold"&20员工名单', orientation='V')

    wb.close()


def print_setting(worksheet, header, orientation='H'):
    if orientation == 'H':
        worksheet.set_landscape()
    elif orientation == 'V':
        worksheet.set_portrait()

    worksheet.set_paper(9)
    worksheet.center_horizontally()
    worksheet.fit_to_pages(1, 0)
    worksheet.repeat_rows(0)
    worksheet.set_header(header)
    worksheet.set_footer(
        '''&L&"Times New Roman,Regular"&D &T&C&"Times New Roman,Regular"@ CityWok Manager&R&"Times New Roman,Regular"&P/&N''')
