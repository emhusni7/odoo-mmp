from odoo import api, fields, models

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
            'amount': x.amount_fix,
            'qty': x.quantity
        }), self.rule_ids)
        self.rule_mmp_ids.unlink()
        self.rule_mmp_ids = list(data)

HRPayrollStructure

class HRContract(models.Model):
    _inherit = "hr.contract"
    contract_rule_ids = fields.One2many("hr.salary.rule.mmp","contract_id","Rule")

    def action_generate_rule(self):
        data = map(lambda x: (0, 0,{
            'rule_id': x.rule_id.id,
            'contract_id': self.id,
            'name': x.name,
            'amount_type': x.amount_type,
            'amount_python_compute': x.amount_python_compute,
            'amount': x.amount,
            'qty': x.qty
        }), self.struct_id.rule_mmp_ids)
        self.contract_rule_ids.unlink()
        self.contract_rule_ids = list(data)

HRContract