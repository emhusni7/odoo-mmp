from odoo import models, fields

class Department(models.Model):
    _inherit = "department"
    department_code = fields.Char("Code")
