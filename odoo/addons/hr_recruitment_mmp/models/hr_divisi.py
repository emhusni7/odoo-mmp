from odoo import models, fields

class HrDivisi(models.Model):
    _name = 'hr.divisi.mmp'
    _order = 'code'
    name = fields.Char("Nama Divisi", required=1, index=True)
    code = fields.Char("Code", required=1)
    manager = fields.Many2one("hr.employee", "Manager")
    department_id = fields.Many2one("hr.department", "Department", required=1)
    company_id = fields.Many2one("res.company", "Company", default=lambda self: self.env.company)

HrDivisi