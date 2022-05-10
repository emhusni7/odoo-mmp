from odoo import http
from odoo.http import content_disposition, request
from datetime import datetime
import io
import xlsxwriter

class ExcelReportController(http.Controller):

    @http.route(['/hr_recruitement_mmp/excel_report/<model("wiz.ptk.report"):wizard>',], type='http', auth="user", csrf=False)
    def generate_xls_report(self,wizard=None,**args):
        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', content_disposition('ptk_report' + '.xlsx'))
            ]
        )

        # create workbook object from xlsxwriter library
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        # create some style to set up the font type, the font size, the border, and the aligment
        title_style = workbook.add_format({'font_name': 'Times', 'font_size': 14, 'bold': True, 'align': 'center'})
        header_style = workbook.add_format(
            {'font_name': 'Times', 'bold': True, 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'center'})
        text_style = workbook.add_format(
            {'font_name': 'Times', 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'left'})
        date_style = workbook.add_format(
            {'font_name': 'Times', 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'left', 'num_format': 'DD/MM/YYYY'})
        number_style = workbook.add_format(
            {'font_name': 'Times', 'left': 1, 'bottom': 1, 'right': 1, 'top': 1, 'align': 'right'})

        # loop all selected user/salesperson
        for wiz in wizard:
            # create worksheet/tab per salesperson
            sheet = workbook.add_worksheet("Test")
            # set the orientation to landscape
            sheet.set_landscape()
            # set up the paper size, 9 means A4
            sheet.set_paper(9)
            # set up the margin in inch
            sheet.set_margins(0.5, 0.5, 0.5, 0.5)

            # set up the column width
            sheet.set_column('A:A', 5)
            sheet.set_column('B:L', 12)

            # the report title
            # merge the A1 to E1 cell and apply the style font size : 14, font weight : bold
            sheet.merge_range('A1:L1', 'Report PTK', title_style)
            sheet.merge_range('A2:L2', 'Periode %s sd %s'%(wiz.date_from.strftime("%d %B %Y"), wiz.date_to.strftime("%d %B %Y")), title_style)

            # table title
            sheet.write(3, 0, 'No.', header_style)
            sheet.write(3, 1, 'PTK Code', header_style)
            sheet.write(3, 2, 'Request Date', header_style)
            sheet.write(3, 3, 'Department', header_style)
            sheet.write(3, 4, 'Division', header_style)
            sheet.write(3, 5, 'Section', header_style)
            sheet.write(3, 6, 'Sub Section', header_style)
            sheet.write(3, 7, 'Grade', header_style)
            sheet.write(3, 8, 'Level', header_style)
            sheet.write(3, 9, 'Qty', header_style)
            sheet.write(3, 10, 'Status', header_style)

            row = 4
            number = 1
            domain = [('request_date','>=',wiz.date_from),('request_date','<=',wiz.date_to)]

            if wiz.stage_id:
               domain += [('stage_id','=',wiz.stage_id.id)]
            # # search the ptk-mmp
            orders = request.env['ptk.mmp'].search(domain)
            for order in orders:
                # the report content
                sheet.write(row, 0, number, text_style)
                sheet.write(row, 1, order.name, text_style)
                sheet.write(row, 2, order.request_date.strftime("%d %B %Y"), text_style)
                sheet.write(row, 3, order.department_id.name, text_style)
                sheet.write(row, 4, order.divisi_id.name, text_style)
                sheet.write(row, 5, order.sect_id.name, text_style)
                sheet.write(row, 6, order.sub_sect_id.name, text_style)
                sheet.write(row, 7, order.grade.sequence, number_style)
                sheet.write(row, 8, order.level.name, text_style)
                sheet.write(row, 9, order.jml_pengajuan, number_style)
                sheet.write(row, 10, order.stage_id.name, number_style)

                row += 1
                number += 1

            # # create a formula to sum the total sales
            # sheet.merge_range('A' + str(row + 1) + ':D' + str(row + 1), 'Total', text_style)
            # sheet.write_formula(row, 4, '=SUM(E3:E' + str(row) + ')', number_style)

        # return the excel file as a response, so the browser can download it
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

        return response