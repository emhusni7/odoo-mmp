from odoo import models, fields, api

class HrDivisi(models.Model):
    _name = 'hr.divisi.mmp'
    _order = 'code'
    _description = 'Divisi'
    name = fields.Char("Nama Divisi", required=1, index=True)
    code = fields.Char("Code", required=1)
    manager = fields.Many2one("hr.employee", "Manager")
    department_id = fields.Many2one("hr.department", "Department", required=1)
    company_id = fields.Many2one("res.company", "Company", default=lambda self: self.env.company)

HrDivisi

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    divisi_id = fields.Many2one("hr.divisi.mmp","Divisi", required=1, domain="[('department_id','=',department_id)]")

    @api.onchange('department_id')
    def onchange_deparment(self):
        self.divisi_id = False