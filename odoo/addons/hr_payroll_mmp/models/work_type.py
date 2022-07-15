from odoo import fields, models, api
from datetime import datetime, time
import pytz

class WorkUoM(models.Model):
    _name = "hr.work.uom"
    _sql_constraints = [
        ('work_uom_code_uniq', 'unique (code)', """UoM unique Code"""),
        ('work_uom_name_uniq', 'unique (code)', """UoM unique Name"""),
    ]
    code = fields.Char("Code", required=1)
    name = fields.Char("Name", required=1)
WorkUoM

class WorkType(models.Model):
    _name = "hr.work.type"
    _sql_constraints = [
        ('work_type_code_uniq', 'unique (code)', """Type unique Code"""),
        ('work_type_name_uniq', 'unique (name)', """Type unique Name"""),
    ]
    code = fields.Char("Code", size=4, required=1, default="/")
    name = fields.Char("Work Type", required=1)
    price_unit = fields.Float("Price Unit", digits=(16,2), required=1)
    uom_id = fields.Many2one("hr.work.uom", "Uom", required=1)
    active = fields.Boolean("Active", default=True)

    @api.model
    def create(self, vals):
        if vals.get('code') == "/":
            vals['code'] = self.env['ir.sequence'].next_by_code('hr.work.type')
        return super(WorkType, self).create(vals)

WorkType

class WorkEntriesTransaction(models.Model):
    _name = "hr.work.entry"
    _order = "from_date"

    @api.onchange("from_date")
    def _getEmployeeDomain(self):
        if self.from_date:
            self.sudo().env.cr.execute('''
                Select
                    ha.employee_id
                from hr_attendance ha
                where (ha.check_in + interval '7 hours')::Date between %s and %s
                group by ha.employee_id
            ''',(self.from_date, self.from_date))
            ids = self.sudo().env.cr.fetchall()
            return {
                'value': {
                  'employee_id': False
                },
                'domain': {
                    'employee_id': [('id','in',[x[0] for x in ids])]
                }
            }

        return {
            'value': {
                'employee_id': False
            },
            'domain': {
                'employee_id': [('id','=',0)]
            }
        }

    @api.model
    def create(self, vals):
        if vals.get('name') == "/":
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.work.entry')
        return super(WorkEntriesTransaction, self).create(vals)

    name = fields.Char("Name", required=1, default="/", copy=False)
    from_date = fields.Date("From Date", required=1)
    work_type = fields.Many2one("hr.work.type","Work Type", required=1)
    employee_id = fields.Many2one("hr.employee","Employee",required=1)
    qty = fields.Float("Qty", digits=(16,2))
    uom_id = fields.Many2one("hr.work.uom", related="work_type.uom_id", string="UoM")
    price_unit = fields.Float("Price Unit",related="work_type.price_unit", store=True, digits=(16,2))
    price_total = fields.Float("Price Total", digits=(16,2))

    @api.onchange('qty')
    def onchange_qty(self):
        self.price_total = round(self.price_unit * self.qty,2)

WorkEntriesTransaction