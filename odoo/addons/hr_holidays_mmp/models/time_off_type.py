from odoo import models, fields

class TimeOffType(models.Model):
    _inherit = "hr.leave.type"
    libur = fields.Selection([('y','Ya'),('t','Tidak')],"Hari Libur", default='t', required=1)

TimeOffType

class AllocationType(models.Model):
    _inherit = "hr.leave.allocation"
    holiday_type = fields.Selection(selection=[('employee', 'By Employee')],
        string='Allocation Mode', readonly=True, required=True, default='employee',
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
        help="Allow to create requests in batchs:\n- By Employee: for a specific employee"
             "\n- By Company: all employees of the specified company"
             "\n- By Department: all employees of the specified department"
             "\n- By Employee Tag: all employees of the specific employee group category")

AllocationType