from odoo import models, fields, _
from odoo.exceptions import UserError
import base64, io, csv
from datetime import datetime, timedelta
import re

class WizAbsen(models.Model):
    _name = "wiz.import.absen"

    file_xls = fields.Many2many('ir.attachment', 'wiz_import_absen_rel', 'wiz_id','attachment_id', 'Attachments',
                     help="You may attach files to this template, to be added to all "
                          "emails created from this template")
    file_name = fields.Char("Filename", required=False)

    def import_xls(self):
        attObj = self.env['hr.attendance.mmp']
        try:
            for xyz in self.file_xls:
                csv_data = base64.b64decode(xyz.datas)
                data_file = io.StringIO(csv_data.decode("utf-8"))
                data_file.seek(0)
                csv_reader = csv.reader(data_file, delimiter=',')
                for row in csv_reader:
                    try:
                        dtime = datetime.strptime("%s %s" % (row[3], row[4]), "%Y/%m/%d %H:%M:%S") - timedelta(hours=7)
                    except:
                        raise UserError("Wrong Format Date and time use (YYYY/MM/DD HH:MM:SS)")

                    vals = {
                        'code': row[0],
                        'name': row[1].replace("=", "").replace('"', ""),
                        'type': str(row[2]),
                        'dtime': dtime
                    }
                    attObj.create(vals)
        except FileNotFoundError:
            raise UserError('File Excel Not Found. \n%s.' % self.file_name)

        action = self.env["ir.actions.actions"]._for_xml_id("hr_attendance_mmp.hr_attendance_action_mmp_overview")
        return action

WizAbsen
