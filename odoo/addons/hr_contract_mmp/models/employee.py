from odoo import models, fields, tools, api

class Family(models.Model):
    _name = "family.mmp"
    name = fields.Char("Nama", required=1)
    gender = fields.Selection(selection=[("L","Laki-laki"),('P',"Perempuan")], required=1)
    ttl = fields.Date("Tgl Lahir", required=1)
    status = fields.Selection(selection=[("ayah","Ayah"),("ibu","Ibu"),("suami","Suami"),("istri","Istri"),("anak","Anak")],
                              required=1)
    employee_id = fields.Many2one("hr.employee","Employee", invisible=1, default=lambda self: self.env.context.get('active_id'))

Family

class Education(models.Model):
    _name = "education.mmp"

    def _check_type(self, cr, uid, ids, context=None):
        record = self.browse(cr, uid, ids, context=context)
        for data in record:
            if not (len(str(data.masuk)) != 4 or len(str(data.keluar))) != 4:
                return False
        return True

    _constraints = [(_check_type, 'Error: Field Tahun masuk/keluar harus 4 digit dan numeric', ['masuk','keluar'])]

    name = fields.Char("Nama Sekolah/Perguruan Tinggi", required=1)
    jenjang = fields.Selection(selection=[('sd','SD'),('smp','SMP'),('sma','SMA'),('d3','D3'),('s1','S1'),('s2','S2'),('s3','S3')],required=1)
    masuk = fields.Integer("Tahun Masuk")
    keluar = fields.Integer("Tahun Keluar")
    employee_id = fields.Many2one("hr.employee","Empoyee",invisible=1,default=lambda self: self.env.context.get('active_id'))


Education

class Employee(models.Model):
    _inherit = "hr.employee"

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """ name_search(name='', args=None, operator='ilike', limit=100) -> records

        Search for records that have a display name matching the given
        ``name`` pattern when compared with the given ``operator``, while also
        matching the optional search domain (``args``).

        This is used for example to provide suggestions based on a partial
        value for a relational field. Sometimes be seen as the inverse
        function of :meth:`~.name_get`, but it is not guaranteed to be.

        This method is equivalent to calling :meth:`~.search` with a search
        domain based on ``display_name`` and then :meth:`~.name_get` on the
        result of the search.

        :param str name: the name pattern to match
        :param list args: optional search domain (see :meth:`~.search` for
                          syntax), specifying further restrictions
        :param str operator: domain operator for matching ``name``, such as
                             ``'like'`` or ``'='``.
        :param int limit: optional max number of records to return
        :rtype: list
        :return: list of pairs ``(id, text_repr)`` for all matching records.
        """
        if args == None:
            args = []
        args += ['|',('name','ilike', name),('pin','ilike', name)]
        ids = self._search(args, limit=limit)
        return self.browse(ids).sudo().name_get()

    @api.depends('name', 'pin')
    def name_get(self):
        res = []
        for record in self:
            name = "[%s] %s"%(record.pin or "", record.name)
            res.append((record.id, name))
        return res

    bpjs = fields.Char("No. BPJS")
    npwp = fields.Char("No. NPWP")
    address = fields.Text("Address")
    complete_name = fields.Char("Complete Name", compute="_get_name")
    private_email = fields.Char(string="Private Email", groups="hr.group_hr_user", store=True, readonly=False)
    phone = fields.Char("Private Phone",readonly=False,groups="hr.group_hr_user")
    ptkp_id = fields.Many2one("ptkp", "PTKP", required=0)
    fam_ids = fields.One2many("family.mmp","employee_id","Family Data")
    employee_type = fields.Selection(selection=[
        ('employee','Karyawan Tetap'),
        ('pkwt','PKWT'),
        ('pkwtt','PKWTT'),
        ('bor','Borongan')
    ], string='Employee Type', default='employee', required=True,
        help="The employee type. Although the primary purpose may seem to categorize employees, this field has also an impact in the Contract History. Only Employee type is supposed to be under contract and will have a Contract History.")
    jenis_kerja = fields.Selection(selection=[('5','5 Hari Kerja'),('6','6 Hari Kerja')])
    keahlian = fields.Text("Keahlian")
    pin = fields.Char(string="ID", copy=False, groups=False,
                help="PIN used to Check In/Out in the Kiosk Mode of the Attendance application (if enabled in Configuration) and to change the cashier in the Point of Sale application.")
    work_phone = fields.Char('Work Phone', readonly=False)
    marital = fields.Selection([
        ('single', 'Single'),
        ('married', 'Menikah'),
        ('divorce', 'Cerai'),
    ], string='Marital Status', groups="hr.group_hr_user", default='single', tracking=True)
    education = fields.One2many("education.mmp","employee_id","Education")
    trans_bpjs = fields.One2many("bpjs.kes.contract.mmp",compute="_compute_emp_bpjs",string="BPJS Kesehatan")
    trans_bpjs_k = fields.One2many("bpjs.ket.contract.mmp",compute="_compute_emp_bpjs_k",string="BPJS Ketenaga Kerjaan")

    @api.depends('contract_id.bpjs_kes_tran_ids')
    def _compute_emp_bpjs(self):
        if self.contract_id.bpjs_kes_tran_ids:
            self.trans_bpjs = self.contract_id.bpjs_kes_tran_ids.ids
        else:
            self.trans_bpjs = False

    @api.depends('contract_id.bpjs_ket_tran_ids')
    def _compute_emp_bpjs_k(self):
        if self.contract_id.bpjs_ket_tran_ids:
            self.trans_bpjs_k = self.contract_id.bpjs_ket_tran_ids.ids
        else:
            self.trans_bpjs_k = False

    def action_open_contract_history(self):
        self.ensure_one()
        if self.contract_ids:
            action = self.env["ir.actions.actions"]._for_xml_id('hr_contract.hr_contract_history_view_form_action')
        else:
            action = self.env["ir.actions.actions"]._for_xml_id('hr_contract.hr_contract_history_view_form_action')
        action['res_id'] = self.id
        return action

Employee
