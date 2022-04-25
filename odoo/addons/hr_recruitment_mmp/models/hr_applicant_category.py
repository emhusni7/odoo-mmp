from odoo import models, fields

#Applicant => Company Outsource
class HrApplicantComp(models.Model):
    _inherit = "hr.applicant.category"
    _description = "Company Recruit"

    code = fields.Char("Code", required=True)

    _sql_constraints = [
        ('code_uniq', 'unique (code)', "Code already exists !"),
    ]