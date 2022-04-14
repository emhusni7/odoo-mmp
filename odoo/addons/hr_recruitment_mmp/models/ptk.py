from odoo import models, fields, api
from odoo.exceptions import UserError

class PTK(models.Model):
    _name = "ptk.mmp"

    employee_id = fields.Many2one("hr.employee", "Employee", required=1, default= lambda self: self.get_employee())
    department_id = fields.Many2one("hr.department","Department", required=1)
    divisi_id = fields.Many2one("hr.divisi","Divisi", required=1)
    sect_id = fields.Many2one("hr.job","Section")
    sub_sect_id = fields.Many2one("hr.job","Section")
    team_id = fields.Many2one("team.mmp","Team")
    unit_id = fields.Many2one("unit.mmp","Unit")
    grade = fields.Many2one("hr.recruitment.degree", "Grade", required=1)



    def get_employee(self):
        emp = self.sudo().env['hr.employee'].search([('user_id','=',self.env.uid),('active','=',True)],limit=1).ids
        if emp:
            return emp[0]
        else:
            raise UserError("User Tidak mempunyai Link ke Employee")