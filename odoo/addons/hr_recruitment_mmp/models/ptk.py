from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.http import request

class PTK(models.Model):
    _name = "ptk.mmp"
    _inherit = ['mail.thread']
    _description = "PTK"

    _order = "request_date desc"

    @api.onchange('department_id')
    def get_stage(self):
        rule = self.sudo().department_id.rule_ids.filtered(lambda x: x.employee_id.id in self.env.user.employee_ids.ids and x.stage_id.name in ['User','Manager']).sorted(lambda x: x.sequence)
        if rule:
            self.stage_id = rule[0].stage_id.id
        else:
            stage_id = self.sudo().env['hr.recruitment.stage'].search([('name','=','User')]).ids[0]
            self.stage_id = stage_id

    name = fields.Char("Name", readonly=1, default='/')
    request_date = fields.Date("Request Date", default= fields.Date.today(), required=1)
    stage_id = fields.Many2one("hr.recruitment.stage","Stage", required=1, default= lambda self: self.get_stage, track_visibility="onchange")
    stage_name = fields.Char("Stage", related='stage_id.name')
    employee_id = fields.Many2one("hr.employee", "Request By", required=1, default= lambda self: self.get_employee())
    department_id = fields.Many2one("hr.department","Department" ,required=1)
    divisi_id = fields.Many2one("hr.divisi.mmp","Divisi", required=1, domain="[('department_id','=',department_id)]")
    sect_id = fields.Many2one("hr.job","Section", domain="[('divisi_id','=',divisi_id)]")
    sub_sect_id = fields.Many2one("hr.job","Sub Section", domain="[('parent_sec_id','=',sect_id)]")
    team_id = fields.Many2one("team.mmp","Team")
    unit_id = fields.Many2one("unit.mmp","Unit", domain="[('team_id','=',team_id)]")
    grade = fields.Many2one("hr.recruitment.degree", "Grade", required=1)
    level = fields.Many2one("hr.level","Level", required=1, domain="[('grade_categ','=',grade)]")
    type_ptk = fields.Many2one("hr.applicant.refuse.reason","Type PTK", domain=[('template_id','=',False)],required=1)
    pendidikan = fields.Selection([("sma","SMA/SMK"),("d3","D3"),("s1","S1"),("s2","S2"),("s3","S3")],"Pendidikan",required=1, track_visibility="onchange")
    jurusan = fields.Char("Kualikasi Jurusan", required=1)
    pengalaman = fields.Integer("Pengalaman Kerja", default=0,required=1)
    jml_pengajuan = fields.Integer("Jumlah Pengajuan", default=1, required=1, track_visibility="onchange")
    tgl_butuh = fields.Date("Tanggal Butuh",required=1)
    penempatan = fields.Selection([("os","Under OS"),("pt","Under PT")],"Penempatan", required=1)
    gaji = fields.Selection([("monthly","Monthly Base"),("out","Output Base"),("time","Time Base")],"Basis Penggajian", required=1)
    type_pekerja = fields.Selection([("do","Direct (Produksi) - Operator"),
                                 ("ds","Direct (Produksi) - Service"),
                                 ("ila","Indirect (Non-Produksi) - Lapangan A"),
                                 ("ilb","Indirect (Non-Produksi) - Lapangan B"),
                                 ("ik", "Indirect (Non-Produksi) - Kantor"),
                                 ], "Category", required=1)
    type_apd = fields.Char("Type APD",compute="_compute_apd")
    wl_id = fields.Many2one("hr.work.location","Work Lokasi", required=1)
    contract = fields.Selection([('pkwt','PKWT'),('pkwtt','PKWTT')],"Type Kontrak", required=1)
    mcu = fields.Selection([('bs','Basic'),('bs_p','Basic Plus'),('prem','Premium')],"Type MCU", required=1)
    h_kerja = fields.Selection([('5','5 Hari'),('6','6 Hari')],"Hari Kerja", required=1)
    shift = fields.Selection([('s','Shift'),('ns','Non Shift')],"Shift", required=1)
    j_k = fields.Char("Jam Kerja", size=3, required=1)
    fit_ids = fields.Many2many("fasilitas.it.mmp","ptk_fasilitas_mmp_rel","ptk_id","fas_id","Fasilitas IT",required=1)
    fit_ket = fields.Text("Keterangan (Fasilitas IT)")
    list_k = fields.Text("List Karyawan yg Resign/Mutasi/Demosi")
    kriteria = fields.Text("Kriteria", required=1)
    job_desc = fields.Text("Job Desc", required=1)
    link_login = fields.Char("Link")
    invisible_stage = fields.Boolean("Invisible",compute="_compute_inv")
    jml_pemenuhan = fields.Integer("Sudah Dipenuhi", store=True, compute="_compute_pemenuhan")
    employee_ids = fields.One2many("hr.employee", "ptk_id", "Employee")
    ptk_app_ids = fields.One2many("mail.tracking.value", compute="_compute_approval", string="Approval")
    jml_pengajuan_dummy = fields.Integer("Jml Pengajuan", related="jml_pengajuan")
    pemenuhan_ids = fields.One2many("ptk.pemenuhan", "ptk_id", "Pemenuhan")
    emp_created = fields.Integer("Emp Created", store=True, compute="_compute_emp_created")

    @api.depends('pemenuhan_ids', 'pemenuhan_ids.employee_ids')
    def _compute_emp_created(self):
        for x in self:
            x.emp_created = len(x.employee_ids)

    def _compute_approval(self):
        self.ptk_app_ids = self.env['mail.tracking.value'].search([('mail_message_id.model','=','ptk.mmp'),
                                                                   ('field_desc','=','Stage'),
                                                                   ('mail_message_id.res_id', '=', self.id),
                                                                   ], order='write_date')
    @api.depends('pemenuhan_ids')
    def _compute_pemenuhan(self):
        self.jml_pemenuhan = sum([x.jml_pemenuhan for x in self.pemenuhan_ids])
        if self.jml_pengajuan <= self.jml_pemenuhan and self.stage_name == 'Recruitment':
           stage_id = self.sudo().env['hr.recruitment.stage'].search([('name', '=', 'Complete')], limit=1)
           if stage_id:
               self.stage_id = stage_id.id
        elif self.jml_pengajuan > self.jml_pemenuhan and self.stage_name == 'Complete':
           stage_id = self.sudo().env['hr.recruitment.stage'].search([('name', '=', 'Recruitment')], limit=1)
           if stage_id:
               self.stage_id = stage_id.id

    def act_view_ptk(self):
        action = self.env["ir.actions.actions"]._for_xml_id("hr.open_view_employee_list_my")
        action['context'] = {
            'default_res_model': self._name,
            'default_ptk_id': self.id,
            'default_department_id': self.department_id.id,
            'default_divisi_id': self.divisi_id.id,
            'default_job_id': self.sect_id.id
        }
        action['domain'] = [('ptk_id','=', self.id)]
        return action

    def unlink(self):
        for x in self:
            if x.stage_name.lower() not in ['reject','user']:
                raise UserError("Delete Record hanya bisa dilakukan di stage User / Reject")
        return super(PTK, self).unlink()

    def print_report(self):
        data = {
            'model_id': self.id,
            'name': self.name,
        }
        return self.env.ref('hr_recruitment_mmp.action_report_ptk').report_action(self)

    def set_cancel(self):
        rule = self.sudo().env['hr.recruitment.stage'].search([('sequence','=',0)]).ids
        if rule:
            self.stage_id = rule[0]

    @api.depends('stage_id')
    def _compute_inv(self):
        self.invisible_stage = True
        rule = self.sudo().department_id.rule_ids.filtered(lambda x: x.stage_id.id == self.stage_id.id and x.employee_id.id in self.env.user.employee_ids.ids).sorted(lambda x: x.sequence)
        if rule:
            for rl in rule:
                self.invisible_stage = False
                break
        elif self.stage_id.sequence == 1:
            self.invisible_stage = False


    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('ptk.mmp.sec')
        return super(PTK, self).create(vals)

    def send_approval(self, now_stage):
        for state in now_stage.sorted(lambda x: x.sequence):
            if state.employee_id in self.env.user.employee_ids:
                self.stage_id = state.next_stage_id.id
                break
            elif not state.employee_id:
                self.stage_id = state.next_stage_id.id
                break


    def send_mail(self):
        now_stage = self.department_id.get_now_stage(self.stage_id)
        nextstage = self.department_id.get_next_stage_email(now_stage)
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        self.link_login="{}/web?db={}#id={}&view_type=form&model={}".format(base_url, self.sudo().env.cr.dbname, self.id, 'ptk.mmp')
        if nextstage:
            template = nextstage and nextstage[0].stage_id.template_id or False
            if template:
                email_to = [x.email_to for x in nextstage]
                if email_to:
                    self.send_approval(now_stage)
                    receipt_list = ';'.join(email_to)
                    email_values = {'email_to': receipt_list}
                    template.sudo().send_mail(self.id, email_values=email_values, force_send=True)

                else:
                    self.send_approval(now_stage)

    @api.onchange('department_id')
    def onchange_dep(self):
        if self.env.user.has_group ('hr_recruitment.group_hr_recruitment_manager'):
            return {
                'value':{'divisi_id': False},
                'domain':
                    {'department_id': [('active', '=', True)]}
                    }
        else:
            return {
                'value': {'divisi_id': False},
                'domain':
                    {'department_id': [('id', '=', self.env.user.employee_id.department_id.id)]}}

    @api.onchange('team_id')
    def onchange_team(self):
        self.unit_id = False

    @api.onchange('divisi_id')
    def onchange_divisi(self):
        return {
            'value': {'sect_id':False}
        }

    @api.depends('type_pekerja')
    def _compute_apd(self):
        for x in self:
            if x.type_pekerja:
               val = dict(x.fields_get(allfields=['type_pekerja'])['type_pekerja']['selection'])[x.type_pekerja]
               x.type_apd = val
            else:
                x.type_apd = False

    @api.onchange('sect_id', 'sub_sect_id')
    def _onchange_section(self):
        if not self.sub_sect_id:
            return {
                'value': {
                    'team_id': False
                },
                'domain': {'team_id': [('section_id', '=', self.sect_id.id)]}
            }
        return {
            'value': {'team_id': False},
            'domain':
                {'team_id': [('sub_section_id', '=', self.sub_sect_id.id)]}}

    @api.onchange('sect_id')
    def onchange_sect(self):
        self.sub_sect_id = False

    @api.onchange('grade')
    def onchange_grade(self):
        self.level = False

    def get_employee(self):
        emp = self.sudo().env['hr.employee'].search([('user_id','=',self.env.uid),('active','=',True)],limit=1).ids
        if emp:
            return emp[0]
        else:
            raise UserError("User Tidak mempunyai Link ke Employee")
PTK

class PTKPemenuhan(models.Model):
    _name = 'ptk.pemenuhan'
    _rec_name = 'tgl_pemenuhan'

    ptk_id = fields.Many2one("ptk.mmp","PTK No")
    jml_pemenuhan = fields.Integer("Jml Pemenuhan", required=1)
    tgl_pemenuhan = fields.Date("Tgl", required=1)
    count_emp = fields.Integer("Emp. Created", compute="_compute_emp")
    employee_ids = fields.One2many("hr.employee","ptk_pemenuhan_id", "PTK Pemenuhan")

    def _compute_emp(self):
        for x in self:
            x.count_emp = len(x.employee_ids)

    def unlink(self):
        if self.count_emp > 0:
            raise UserError("Cannot Be Delete When Employee From PTK Has Been Created From this Document")
        return super(PTKPemenuhan, self).unlink()

    @api.constrains('jml_pemenuhan')
    def _check_pemenuhan(self):
        if self.ptk_id.jml_pemenuhan > self.ptk_id.jml_pengajuan:
            raise UserError(_("Jumlah Pengajuan Karyawan > Jumlah Pemenuhan"))

    def act_pemenuhan(self):
        action = self.env["ir.actions.actions"]._for_xml_id("hr.open_view_employee_list_my")
        action['context'] = {
            'default_res_model': self._name,
            'default_res_id': self.ids[0],
            'default_ptk_id': self.ptk_id.id,
            'default_ptk_pemenuhan_id': self.id,
            'default_department_id': self.ptk_id.department_id.id,
            'default_divisi_id': self.ptk_id.divisi_id.id,
            'default_job_id': self.ptk_id.sect_id.id,
            'jml_pemenuhan': self.jml_pemenuhan,
            'count_emp': self.count_emp
        }
        action['domain'] = [('ptk_id','=', self.ptk_id.id),('ptk_pemenuhan_id','=', self.id)]
        return action

PTKPemenuhan

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    ptk_id = fields.Many2one("ptk.mmp","No. PTK")
    ptk_pemenuhan_id = fields.Many2one("ptk.pemenuhan","PTK Pemenuhan", domain="[('ptk_id','=',ptk_id)]")

    @api.model
    def create(self, vals_list):
        if self._context.get("default_res_model") == 'ptk.mmp':
            raise UserError("Tidak Bisa Create Employee tanpa melaui Pemenuhan")
        if self._context.get("default_res_model") == 'ptk.pemenuhan':
            if self._context.get('jml_pemenuhan') < self._context.get('count_emp') + 1:
                raise UserError("Employee telah melebihi PTK")
        res = super(HrEmployee, self).create(vals_list)
        return res