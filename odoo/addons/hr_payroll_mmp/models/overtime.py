from odoo import models, fields

class Overtime(models.Model):
    _inherit = "hr.overtime"
    input_id = fields.Many2one("hr.payslip.input", "Input")
Overtime
