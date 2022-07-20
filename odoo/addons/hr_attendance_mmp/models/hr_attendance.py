from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HrAttendance(models.Model):
    _name = "hr.attendance.mmp"
    _description = "Attendance MMP"
    _order = "dtime, name desc"

    code = fields.Char("Code Mesin", required=1)
    name = fields.Char("No.ID", required=1, index=True)
    type = fields.Selection([('1','In'),('0','Out')],'Check In/Out', required=1)
    dtime = fields.Datetime("Date Time", required=1)
    has_attd = fields.Many2one("hr.attendance", "Attd")

HrAttendance
