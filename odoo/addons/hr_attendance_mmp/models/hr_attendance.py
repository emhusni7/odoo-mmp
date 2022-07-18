from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HrAttendance(models.Model):
    _name = "hr.attendance.mmp"
    _description = "Attendance MMP"
    _order = "dtime, employee_id desc"

    _sql_constraints = [('code_name_type_dtime_mmp', 'unique(code,name,type,dtime)', 'Attendance Data must be unique')]

    code = fields.Char("Code Mesin", required=1)
    name = fields.Char("No.ID", required=1)
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True,
                                  ondelete='cascade', index=True)
    department_id = fields.Many2one('hr.department', string="Department", related="employee_id.department_id",
                                    readonly=True)
    type = fields.Selection([('1','In'),('0','Out')],'Check In/Out', required=1)
    dtime = fields.Datetime("Date Time", required=1)
    has_attd = fields.Many2one("hr.attendance", "Attd")

HrAttendance
