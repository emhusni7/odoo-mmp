from odoo import models, fields
from odoo.exceptions import UserError
import base64, io, csv
from datetime import datetime, timedelta

class WizAbsen(models.Model):
    _name = "wiz.import.absen"

    file_xls = fields.Binary("Upload Csv", required=1)
    file_name = fields.Char("Filename", required=1)

    def import_xls(self):
        try:
            csv_data = base64.b64decode(self.file_xls)
            data_file = io.StringIO(csv_data.decode("utf-8"))
            data_file.seek(0)
            csv_reader = csv.reader(data_file, delimiter=',')
        except FileNotFoundError:
            raise UserError('File Excel Not Found. \n%s.' % self.file_name)

        empObj = self.env['hr.employee']
        attObj = self.env['hr.attendance.mmp']

        for row in csv_reader:
            rfid = row[1]
            emp = empObj.search([('barcode','=',rfid)], limit=1)
            if not emp:
                raise UserError('Employee with RFID %s Not Found', rfid)
            try:
                dtime = datetime.strptime("%s %s"%(row[3],row[4]),"%Y/%m/%d %H:%M:%S") - timedelta(hours=7)
            except:
                raise UserError("Wrong Format Date and time use (yyyy/mm/dd hh:mm:ss)")

            vals = {
                'code': row[0],
                'name': row[1],
                'employee_id': emp.id,
                'type': str(row[2]),
                'dtime': dtime
            }
            attObj.create(vals)
        action = self.env["ir.actions.actions"]._for_xml_id("hr_attendance_mmp.hr_attendance_action_mmp_overview")
        return action

WizAbsen
