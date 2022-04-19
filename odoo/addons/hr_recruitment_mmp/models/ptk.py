from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PTK(models.Model):
    _name = "ptk.mmp"
    _description = "PTK"

    name = fields.Char("Name", readonly=1, default='/')
    employee_id = fields.Many2one("hr.employee", "Employee", required=1, default= lambda self: self.get_employee())
    department_id = fields.Many2one("hr.department","Department" ,required=1)
    divisi_id = fields.Many2one("hr.divisi.mmp","Divisi", required=1, domain="[('department_id','=',department_id)]")
    sect_id = fields.Many2one("hr.job","Section", domain="[('divisi_id','=',divisi_id)]")
    sub_sect_id = fields.Many2one("hr.job","Sub Section", domain="[('parent_sec_id','=',sect_id)]")
    team_id = fields.Many2one("team.mmp","Team")
    unit_id = fields.Many2one("unit.mmp","Unit", domain="[('team_id','=',team_id)]")
    grade = fields.Many2one("hr.recruitment.degree", "Grade", required=1)
    level = fields.Many2one("hr.level","Level", required=1, domain="[('grade_categ','=',grade)]")
    type_ptk = fields.Many2one("hr.applicant.refuse.reason","Type PTK", domain=[('template_id','=',False)],required=1)
    pendidikan = fields.Selection([("sma","SMA/SMK"),("d3","D3"),("s1","S1"),("s2","S2"),("s3","S3")],"Pendidikan",required=1)
    jurusan = fields.Char("Kualikasi Jurusan", required=1)
    pengalaman = fields.Integer("Pengalaman Kerja", default=0,required=1)
    jml_pengajuan = fields.Integer("Jumlah Pengajuan", default=1, required=1)
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

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('ptk.mmp.sec')
        return super(PTK, self).create(vals)

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