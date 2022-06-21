from odoo import fields, models, api

class HRSalaryRule(models.Model):
    _inherit = "hr.salary.rule"
    h_insurance = fields.Boolean("Healt Insurance", default=False)
    w_insurance = fields.Boolean("Work Insurance", default=False)
HRSalaryRule

class SalaryRuleMMP(models.Model):
    _name = "hr.salary.rule.mmp"

    name = fields.Char("Code")
    rule_id = fields.Many2one("hr.salary.rule", "Salary Rule")
    struct_id = fields.Many2one("hr.payroll.structure","Struct")
    contract_id = fields.Many2one("hr.contract", "Contract")
    amount_type = fields.Selection([('percentage','Persentase %'),
                                    ('fix', 'Fixed Amount'),
                                    ('code','Python Code')])
    amount_python_compute = fields.Text("Python Code")
    qty = fields.Float('Qty',default=1, digits=(16,2))
    amount = fields.Float('Amount', digits=(16,2), default=1)
    h_insurance = fields.Boolean("Healt Insurance", default=False)
    w_insurance = fields.Boolean("Work Insurance", default=False)

SalaryRuleMMP

class HRPayrollStructure(models.Model):
    _inherit = "hr.payroll.structure"

    rule_mmp_ids = fields.One2many("hr.salary.rule.mmp","struct_id","Generate Rule")

    def action_generate_rule(self):
        data = map(lambda x: (0, 0,{
            'rule_id': x.id,
            'struct_id': self.id,
            'name': x.code,
            'amount_type': x.amount_select,
            'amount_python_compute': x.amount_python_compute,
            'h_insurance': x.h_insurance,
            'w_insurance': x.w_insurance,
            'amount': x.amount_fix,
            'qty': x.quantity
        }), self.rule_ids)
        self.rule_mmp_ids.unlink()
        self.rule_mmp_ids = list(data)

HRPayrollStructure

class HRContract(models.Model):
    _inherit = "hr.contract"
    contract_rule_ids = fields.One2many("hr.salary.rule.mmp","contract_id","Rule")
    wage = fields.Monetary('Total Salary', compute='compute_wage', default=0 ,help="Employee's Net Salary.", readonly=True, store=True)

    @api.depends('contract_rule_ids')
    def compute_wage(self):
        amount = 0
        for trx in self.contract_rule_ids:
            if trx.rule_id.category_id.code != 'DED':
                amount += trx.amount
            else:
                amount -=trx.amount
        self.wage = amount

        self.bpjs_kes_tran_ids.onchange_bpjs_kes()
        self.bpjs_ket_tran_ids.onchange_bpjs_ket()



    def action_generate_rule(self):
        data = map(lambda x: (0, 0,{
            'rule_id': x.rule_id.id,
            'contract_id': self.id,
            'name': x.name,
            'amount_type': x.amount_type,
            'amount_python_compute': x.amount_python_compute,
            'amount': x.amount,
            'h_insurance': x.h_insurance,
            'w_insurance': x.w_insurance,
            'qty': x.qty
        }), self.struct_id.rule_mmp_ids)
        self.contract_rule_ids.unlink()
        self.contract_rule_ids = list(data)

HRContract

class BPJSKesContractMMp(models.Model):
    _inherit = "bpjs.kes.contract.mmp"

    @api.onchange('bpjs_kes_id')
    def onchange_bpjs_kes(self):
        super(BPJSKesContractMMp, self).onchange_bpjs_kes()
        for kes in self:
            kes.grand_total = sum([x.amount for x in kes.contract_id.contract_rule_ids if x.h_insurance])
            kes.amount_company = round(kes.rate_company/100 * min(kes.grand_total,kes.max_wages),2)
            kes.amount_employee = round(kes.rate_employee/100 * min(kes.grand_total,kes.max_wages),2)

BPJSKesContractMMp

class BPJSKetContractMMp(models.Model):
    _inherit = "bpjs.ket.contract.mmp"

    @api.onchange('bpjs_ket_id')
    def onchange_bpjs_ket(self):
        super(BPJSKetContractMMp, self).onchange_bpjs_ket()
        for ket in self:
            ket.grand_total = sum([x.amount for x in ket.contract_id.contract_rule_ids if x.w_insurance])
            ket.amount_jht = round(ket.rate_jht / 100 * min(ket.grand_total, ket.max_wages), 2)
            ket.amount_jht_emp = round(ket.rate_jht_emp / 100 * min(ket.grand_total, ket.max_wages), 2)
            ket.amount_jp = round(ket.rate_jp / 100 * min(ket.grand_total, ket.max_wages), 2)
            ket.amount_jp_emp = round(ket.rate_jp_emp / 100 * min(ket.grand_total, ket.max_wages), 2)
            ket.amount_jkk = round(ket.rate_jkk / 100 * min(ket.grand_total, ket.max_wages), 2)
            ket.amount_jkm = round(ket.rate_jkm / 100 * min(ket.grand_total, ket.max_wages), 2)

