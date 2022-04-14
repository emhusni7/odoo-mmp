from odoo import models, fields,api

class Job(models.Model):
    _inherit = "hr.job"
    _sql_constraints = [
        ('job_name_uniq', 'unique (name)', """Only one value can be defined for each given usage!"""),
        ('job_code_uniq', 'unique (code)', """Only one value can be defined for each given usage!"""),
    ]
    code = fields.Char("Section Code", required=1)
    is_sub = fields.Boolean("is Sub Section", compute="_compute_sub", store=True)
    divisi_id = fields.Many2one("hr.divisi.mmp","Divisi", domain="[('department_id','=',department_id)]", required=1)
    parent_sec_id = fields.Many2one("hr.job", "Parent Section", domain="[('divisi_id','=',divisi_id)]")

    @api.depends('parent_sec_id')
    def _compute_sub(self):
        for x in self:
            if x.parent_sec_id:
                x.is_sub = True
            else:
                x.is_sub = False

class Team(models.Model):
    _name = "team.mmp"
    _sql_constraints = [
        ('team_name_uniq', 'unique (name)', """Only one value can be defined for each given usage!"""),
        ('team_code_uniq', 'unique (code)', """Only one value can be defined for each given usage!"""),
    ]
    code = fields.Char("Team Code", required=1)
    name = fields.Char("Team Name", required=1)
    department_id = fields.Many2one("hr.department","Department", required=1)
    divisi_id = fields.Many2one("hr.divisi.mmp", "Divisi", domain="[('department_id','=',department_id)]",required=1)
    section_id = fields.Many2one("hr.job", "Section" , domain="[('divisi_id','=',divisi_id)]", required=1)
    sub_section_id = fields.Many2one("hr.job", "Sub Section" , domain="[('divisi_id','=',divisi_id),('parent_sec_id','=',section_id)]")

class Unit(models.Model):
    _name = "unit.mmp"

    code = fields.Char("Unit Code", required=1)
    name = fields.Char("Unit Name", required=1)
    department_id = fields.Many2one("hr.department", "Department", required=1)
    divisi_id = fields.Many2one("hr.divisi.mmp", "Divisi", domain="[('department_id','=',department_id)]", required=1)
    section_id = fields.Many2one("hr.job", "Section", domain="[('divisi_id','=',divisi_id)]", required=1)
    sub_section_id = fields.Many2one("hr.job", "Sub Section",
                                     domain="[('divisi_id','=',divisi_id),('parent_sec_id','=',section_id)]")
    team_id = fields.Many2one('team.mmp', 'Team', required=1)

    @api.onchange('section_id','sub_section_id')
    def _onchange_section(self):
        if not self.sub_section_id:
            return {
                'domain':
                    {'team_id': [('section_id', '=', self.section_id.id)]}}
        return {
            'domain':
                {'team_id': [('sub_section_id', '=', self.sub_section_id.id)]}}


