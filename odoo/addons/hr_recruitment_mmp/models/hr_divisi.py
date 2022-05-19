from odoo import models, fields, api

class HrDivisi(models.Model):
    _name = 'hr.divisi.mmp'
    _order = 'code'
    _description = 'Division'
    _sql_constraints = [
        ('division_code_uniq', 'unique (code)', """Division Code Must Be Unique"""),
        ('division_name_uniq', 'unique (name)', """Division Name Must Be Unique"""),
    ]
    name = fields.Char("Nama Division", required=1, index=True)
    code = fields.Char("Code", required=1)
    manager = fields.Many2one("hr.employee", "Manager")
    department_id = fields.Many2one("hr.department", "Department", required=1)
    company_id = fields.Many2one("res.company", "Company", default=lambda self: self.env.company)

    @api.onchange('department_id')
    def onchange_dept(self):
        self.code = "%s."%(self.department_id.code or False)

HrDivisi

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    divisi_id = fields.Many2one("hr.divisi.mmp","Division", required=1, domain="[('department_id','=',department_id)]")

    @api.onchange('department_id')
    def onchange_deparment(self):
        if self.divisi_id:
            if self.divisi_id.department_id.id != self.department_id.id:
                self.divisi_id = False