from odoo import models, fields,api

class Job(models.Model):
    _inherit = "hr.job"
    _rec_name = "complete_name"
    _description = "Section"
    _sql_constraints = [
        ('job_code_uniq', 'unique (code)', """Section Code Must Be Unique"""),
    ]

    complete_name = fields.Char("Complete Name", compute='_compute_name')
    code = fields.Char("Section Code", required=1)
    is_sub = fields.Char("is Sub Section", compute="_compute_sub", store=True)
    divisi_id = fields.Many2one("hr.divisi.mmp","Division", domain="[('department_id','=',department_id)]", required=1)
    parent_sec_id = fields.Many2one("hr.job", "Parent Section", domain="[('divisi_id','=',divisi_id)]")

    @api.depends('code','name')
    def _compute_name(self):
        for x in self:
            x.complete_name = "%s %s"%(x.code, x.name)

    @api.onchange('divisi_id','parent_sec_id')
    def _onchange_divisi(self):
        if not self._context.get('sub_section'):
            self.code = "%s"%(self.divisi_id.code or "")
        else:
            self.code = "%s"%(self.parent_sec_id.code or "")


    @api.depends('parent_sec_id')
    def _compute_sub(self):
        for x in self:
            if x.parent_sec_id:
                x.is_sub = 'Sub Section'
            else:
                x.is_sub = 'Section'

class HrEmployee(models.Model):
    _inherit = "hr.employee"
    job_id = fields.Many2one("hr.job", "Section", domain="[('divisi_id','=',divisi_id)]")

    @api.onchange('divisi_id')
    def onchange_divisi(self):
        if self.job_id:
            if self.job_id.divisi_id.id != self.divisi_id.id:
                self.job_id = False

HrEmployee

class Team(models.Model):
    _name = "team.mmp"
    _rec_name = "complete_name"
    _description = "Team"
    _sql_constraints = [
        ('team_code_uniq', 'unique (code)', """Code Team Must Be Unique"""),
    ]
    code = fields.Char("Team Code", required=1)
    name = fields.Char("Team Name", required=1)
    complete_name = fields.Char("Complete Name", compute='_compute_name')
    department_id = fields.Many2one("hr.department","Department", required=1)
    divisi_id = fields.Many2one("hr.divisi.mmp", "Division", domain="[('department_id','=',department_id)]",required=1)
    section_id = fields.Many2one("hr.job", "Section" , domain="[('divisi_id','=',divisi_id)]", required=1)
    sub_section_id = fields.Many2one("hr.job", "Sub Section" , domain="[('divisi_id','=',divisi_id),('parent_sec_id','=',section_id)]")

    @api.onchange('sub_section_id')
    def onchange_subsect(self):
        self.code = "%s."%(self.sub_section_id.code or "")

    @api.depends('code', 'name')
    def _compute_name(self):
        for x in self:
            x.complete_name = "%s %s" % (x.code, x.name)

    @api.onchange('section_id')
    def onchange_section(self):
        self.sub_section_id = False

    @api.onchange('divisi_id')
    def onchange_divisi(self):
        self.section_id = False

    @api.onchange('department_id')
    def onchange_department(self):
        self.divisi_id = False


class Unit(models.Model):
    _name = "unit.mmp"
    _rec_name = "complete_name"
    _description = "Unit"
    _sql_constraints = [
        ('unit_code_uniq', 'unique (code)', """Unit Code Must Be Unique"""),
    ]

    code = fields.Char("Unit Code", required=1)
    name = fields.Char("Unit Name", required=1)
    complete_name = fields.Char("Complete Name", compute='_compute_name')
    department_id = fields.Many2one("hr.department", "Department", required=1)
    divisi_id = fields.Many2one("hr.divisi.mmp", "Division", domain="[('department_id','=',department_id)]", required=1)
    section_id = fields.Many2one("hr.job", "Section", domain="[('divisi_id','=',divisi_id)]", required=1)
    sub_section_id = fields.Many2one("hr.job", "Sub Section",
                                     domain="[('divisi_id','=',divisi_id),('parent_sec_id','=',section_id)]")
    team_id = fields.Many2one('team.mmp', 'Team', required=1)

    @api.onchange('team_id')
    def onchange_team(self):
        self.code = "%s."%(self.team_id.code or "")

    @api.depends('code', 'name')
    def _compute_name(self):
        for x in self:
            x.complete_name = "%s %s" % (x.code, x.name)

    @api.onchange('section_id')
    def onchange_section(self):
        self.sub_section_id = False

    @api.onchange('divisi_id')
    def onchange_divisi(self):
        self.section_id = False

    @api.onchange('department_id')
    def onchange_department(self):
        self.divisi_id = False

    @api.onchange('section_id','sub_section_id')
    def _onchange_section(self):
        if not self.sub_section_id:
                return {
                'domain':
                    {'team_id': [('section_id', '=', self.section_id.id)]}}
        return {
            'domain':
                {'team_id': [('sub_section_id', '=', self.sub_section_id.id)]}}