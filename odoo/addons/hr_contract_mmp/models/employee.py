from odoo import models, fields, tools, api

class Family(models.Model):
    _name = "family.mmp"
    name = fields.Char("Nama", required=1)
    gender = fields.Selection([("Laki-laki",'L'),("Perempuan",'P')], required=1)
    ttl = fields.Date("Tgl Lahir", required=1)
    status = fields.Selection([("ayah","Ayah"),
                               ("ibu","Ibu"),
                               ("Suami","suami"),
                               ("Istri","istri"),
                               ("Anak","anak")
                               ],"Status", required=1)
    employee_id = fields.Many2one("hr.employee","Employee", invisible=1, default=lambda self: self.env.context.get('active_id'))

Family

# class Education(models.Model):
#     _name = "education.mmp"
#     name = fields.Char("Nama Sekolah/Perguruan Tinggi", required=1)
#     jenjang = fields.
# Education

class Employee(models.Model):
    _inherit = "hr.employee"

    bpjs = fields.Char("No. BPJS")
    npwp = fields.Char("No. NPWP")
    address = fields.Text("Address")
    private_email = fields.Char(string="Private Email", groups="hr.group_hr_user")
    ptkp_id = fields.Many2one("ptkp", "PTKP", required=1)
    fam_ids = fields.One2many("family.mmp","employee_id","Family Data")

Employee
