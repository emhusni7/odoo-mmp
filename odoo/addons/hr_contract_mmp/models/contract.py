from odoo import models, fields, api

class BPJSKesContractMMp(models.Model):
    _name = "bpjs.kes.contract.mmp"

    bpjs_kes_id = fields.Many2one("bpjs.kesehatan.mmp","BPJS Kesehatan", required=1)
    valid_from = fields.Date("Valid From", required=1)
    valid_to = fields.Date("Valid To")
    contract_id = fields.Many2one("hr.contract", "Contract", default= lambda self: self._context.get('default_contract_id'))
    employee_id = fields.Many2one("hr.employee", "Employee", related="contract_id.employee_id")
    rate_company = fields.Float("Rate BPJS Kesehatan Perusahaan (%)",digits=(16,2))
    amount_company = fields.Float("Amount BPJS Kesehatan Perusahaan",digits=(16,2))
    rate_employee = fields.Float("Rate BPJS Kesehatan Peserta(%)", digits=(16,2))
    amount_employee = fields.Float("Amount BPJS Kesehatan Peserta", digits=(16,2))
    grand_total = fields.Float("Grand Total", digits=(16,2))
    max_wages = fields.Float("Max. Gaji Bulanan", digits=(16,2))

    @api.onchange('bpjs_kes_id')
    def onchange_bpjs_kes(self):
        for bpjs in self:
            bpjs.contract_id = self._context.get('default_contract_id')
            bpjs.rate_company = bpjs.bpjs_kes_id.company_rate
            bpjs.rate_employee = bpjs.bpjs_kes_id.employee_rate
            bpjs.max_wages = bpjs.bpjs_kes_id.max_salary

    @api.onchange('rate_company')
    def onchage_rate_company(self):
        self.amount_company = round(self.rate_company / 100 * min(self.grand_total, self.max_wages), 2)

    @api.onchange('rate_employee')
    def onchage_rate_employe(self):
        self.amount_employee = round(self.rate_employee / 100 * min(self.grand_total, self.max_wages), 2)

BPJSKesContractMMp

class BPJSKetContractMMp(models.Model):
    _name = "bpjs.ket.contract.mmp"

    bpjs_ket_id = fields.Many2one("bpjs.ketenagakerjaan.mmp","BPJS KetenagaKerjaan", required=1)
    valid_from = fields.Date("Valid From", required=1)
    valid_to = fields.Date("Valid To")
    contract_id = fields.Many2one("hr.contract", "Contract", default= lambda self: self._context.get('default_contract_id'))
    employee_id = fields.Many2one("hr.employee", "Employee", related="contract_id.employee_id")
    rate_jht = fields.Float("Rate JHT Perusahaan Perusahaan (%)",digits=(16,2), default=0)
    amount_jht = fields.Float("Amount JHT Perusahaan",digits=(16,2))
    rate_jht_emp = fields.Float("Rate JHT Peserta (%)", digits=(16,2))
    amount_jht_emp = fields.Float("Amount JHT Peserta", digits=(16, 2))
    rate_jp = fields.Float("Rate JP Perusahaan (%)", digits=(16,2))
    amount_jp = fields.Float("Amount JP Perusahaan", digits=(16, 2))
    rate_jp_emp = fields.Float("Rate JP Peserta (%)", digits=(16,2))
    amount_jp_emp = fields.Float("Amount JP Perserta", digits=(16,2))
    rate_jkk = fields.Float("Rate JKK (%)", digits=(16,2))
    amount_jkk = fields.Float("Amount JKK", digits=(16, 2))
    rate_jkm = fields.Float("Rate JKM (%)", digits=(16, 2))
    amount_jkm = fields.Float("Amount JKM", digits=(16, 2))
    grand_total = fields.Float("Grand Total", digits=(16,2))
    max_wages = fields.Float("Max. Gaji Bulanan", digits=(16,2))

    @api.onchange('bpjs_ket_id')
    def onchange_bpjs_ket(self):
        self.contract_id = self._context.get('default_contract_id')
        self.rate_jht = self.bpjs_ket_id.rate_jht
        self.rate_jht_emp = self.bpjs_ket_id.rate_jht_emp
        self.rate_jp = self.bpjs_ket_id.rate_jp
        self.rate_jp_emp = self.bpjs_ket_id.rate_jp_emp
        self.rate_jkk = self.bpjs_ket_id.rate_jkk
        self.rate_jkm = self.bpjs_ket_id.rate_jkm
        self.max_wages = self.bpjs_ket_id.max_tot_tunjangan


    @api.onchange('rate_jht','rate_jht_emp')
    def compute_rate_jht(self):
        self.amount_jht = round(self.rate_jht / 100 * min(self.grand_total, self.max_wages), 2)
        self.amount_jht_emp = round(self.rate_jht_emp / 100 * min(self.grand_total, self.max_wages), 2)

    @api.onchange('rate_jp', 'rate_jp_emp')
    def compute_rate_jp(self):
        self.amount_jp = round(self.rate_jp / 100 * min(self.grand_total, self.max_wages), 2)
        self.amount_jp_emp = round(self.rate_jp_emp / 100 * min(self.grand_total, self.max_wages), 2)

    @api.onchange('rate_jkk')
    def compute_rate_jkk(self):
        self.amount_jkk = round(self.rate_jkk / 100 * min(self.grand_total, self.max_wages), 2)

    @api.onchange('rate_jkm')
    def compute_rate_jkm(self):
        self.amount_jkm = round(self.rate_jkm / 100 * min(self.grand_total, self.max_wages), 2)


BPJSKetContractMMp


class Contract(models.Model):
    _inherit = "hr.contract"

    bpjs_kes_tran_ids = fields.One2many("bpjs.kes.contract.mmp","contract_id", "BPJS Kesehatan")
    bpjs_ket_tran_ids = fields.One2many("bpjs.ket.contract.mmp", "contract_id", "BPJS Ketenagakerjaan")
    department_id = fields.Many2one("hr.department", compute='get_department', readonly=1)
    job_id = fields.Many2one("hr.job", compute='get_job', readonly=1)

    @api.depends('employee_id.department_id')
    def get_department(self):
        self.department_id = self.employee_id.department_id.id

    @api.depends('employee_id.job_id')
    def get_job(self):
        self.job_id = self.employee_id.job_id.id