from odoo import models, fields, api, tools

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
            # bpjs.contract_id = self._context.get('default_contract_id')
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
        # self.contract_id = self._context.get('default_contract_id')
        for ket in self:
            ket.rate_jht = ket.bpjs_ket_id.rate_jht
            ket.rate_jht_emp = ket.bpjs_ket_id.rate_jht_emp
            ket.rate_jp = ket.bpjs_ket_id.rate_jp
            ket.rate_jp_emp = ket.bpjs_ket_id.rate_jp_emp
            ket.rate_jkk = ket.bpjs_ket_id.rate_jkk
            ket.rate_jkm = ket.bpjs_ket_id.rate_jkm
            ket.max_wages = ket.bpjs_ket_id.max_tot_tunjangan


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

    name = fields.Char("Name",required=1, default="/")
    bpjs_kes_tran_ids = fields.One2many("bpjs.kes.contract.mmp","contract_id", "BPJS Kesehatan")
    bpjs_ket_tran_ids = fields.One2many("bpjs.ket.contract.mmp", "contract_id", "BPJS Ketenagakerjaan")
    department_id = fields.Many2one("hr.department", compute='get_department', readonly=1)
    job_id = fields.Many2one("hr.job", compute='get_job', readonly=1)
    schedule_ids = fields.One2many("hr.contract.schedule","contract_id", "Schedule")

    @api.model
    def create(self, vals):
        if vals.get('name') == "/":
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.contract')
        return super(Contract, self).create(vals)

    @api.depends('employee_id.department_id')
    def get_department(self):
        self.department_id = self.employee_id.department_id.id

    @api.depends('employee_id.job_id')
    def get_job(self):
        self.job_id = self.employee_id.job_id.id


    def get_contract_schedule_work_hours(self, contract, date_s):

        Cschedule = contract.schedule_ids.filtered(lambda x: x.date_from >= date_s.date() and x.date_to <= date_s)
        schedule = contract.resource_calendar_id
        if Cschedule:
            schedule = Cschedule[0].resource_calendar_id
        attd = schedule.attendance_ids.filtered(lambda x: eval(x.dayofweek) == date_s.weekday())
        if attd:
            return attd[0].work_hours
        return 0

class HrContractHistory(models.Model):
    _inherit = "hr.contract.history"

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        # Reference contract is the one with the latest start_date.
        self.env.cr.execute("""CREATE or REPLACE VIEW %s AS (
            WITH contract_information AS (
                SELECT DISTINCT employee_id,
                                company_id,
                                FIRST_VALUE(id) OVER w_partition AS id,
                                MAX(CASE
                                    WHEN state='open' THEN 1
                                    WHEN state='draft' AND kanban_state='done' THEN 1
                                    ELSE 0 END) OVER w_partition AS is_under_contract
                FROM   hr_contract AS contract
                WHERE  contract.state <> 'cancel'
                AND contract.active = true
                WINDOW w_partition AS (
                    PARTITION BY contract.employee_id
                    ORDER BY
                        CASE
                            WHEN contract.state = 'open' THEN 0
                            WHEN contract.state = 'draft' THEN 1
                            WHEN contract.state = 'close' THEN 2
                            ELSE 3 END,
                        contract.date_start DESC
                    RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
                )
            )
            SELECT     employee.id AS id,
                       employee.id AS employee_id,
                       employee.active AS active_employee,
                       contract.id AS contract_id,
                       contract_information.is_under_contract::bool AS is_under_contract,
                       employee.first_contract_date AS date_hired,
                       %s
            FROM       hr_contract AS contract
            INNER JOIN contract_information ON contract.id = contract_information.id
            RIGHT JOIN hr_employee AS employee
                ON  contract_information.employee_id = employee.id
                AND contract.company_id = employee.company_id
            WHERE   employee.employee_type IN ('employee', 'pkwt', 'pkwtt', 'bor')
        )""" % (self._table, self._get_fields()))