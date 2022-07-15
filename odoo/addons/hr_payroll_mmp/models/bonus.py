from odoo import fields, models, api
from odoo.exceptions import  UserError

class Bonus(models.Model):
    _name = "hr.bonus"

    name = fields.Char("Name", required=1, default="/",  readonly=True)
    date = fields.Date("Date", required=1)
    department_id = fields.Many2one("hr.department", "Department", required=1)
    line_ids = fields.One2many("hr.bonus.line", "bonus_id", "Bonus")
    state = fields.Selection([("draft", "New"), ("confirm", "Confirm")], "State", default="draft")
    divisi_id = fields.Many2one("hr.divisi.mmp","Divisi")

    def unlink(self):
        for x in self:
            if self.state == 'confirm':
                     raise UserError("Cannot Delete Confirm State")
        return super(Bonus, self).unlink()

    def set_confirm(self):
        self.state = "confirm"

    def set_draft(self):
        self.state = "draft"

    @api.model
    def create(self,vals):
        if vals.get('name') == "/":
            vals['name'] = self.env["ir.sequence"].next_by_code("hr.bonus")
        return super(Bonus, self).create(vals)

Bonus

class BonusLine(models.Model):
    _name = "hr.bonus.line"

    @api.model
    def default_get(self, fields):
        result = super(BonusLine, self).default_get(fields)
        if self.env.context.get('department_id'):
            result['department_id'] = self._context.get("department_id")
        if self._context.get('divisi_id'):
            result['divisi_id'] = self._context.get("divisi_id")
        return result

    @api.onchange('divisi_id','department_id')
    def onchange_divdep(self):
        if self.divisi_id:
            return {
                'domain': {
                    'employee_id': [('divisi_id','=',self.divisi_id.id)]
                }
            }
        else:
            return {
                'domain': {
                    'employee_id': [('department_id', '=', self.department_id.id)]
                }
            }
    name = fields.Char("Description", required=1)
    department_id = fields.Many2one("hr.department", "Department")
    divisi_id = fields.Many2one("hr.divisi.mmp", "Divisi")
    employee_id = fields.Many2one("hr.employee", "Employee", required=1)
    bonus_id = fields.Many2one("hr.bonus", "Bonus", ondelete='cascade')
    total_bonus = fields.Float("Bonus", digits=(16,2))

BonusLine