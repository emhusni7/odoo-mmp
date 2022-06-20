from odoo import fields, models, api

class WorkUoM(models.Model):
    _name = "hr.work.uom"
    code = fields.Char("Code", required=1)
    name = fields.Char("Name", required=1)
WorkUoM

class WorkType(models.Model):
    _name = "hr.work.type"

    code = fields.Char("Code", size=4, required=1)
    name = fields.Char("Work Type", required=1)
    price_unit = fields.Float("Price Unit", digits=(16,2), required=1)
    uom_id = fields.Many2one("hr.work.uom", "Uom", required=1)

WorkType

class WorkEntriesTransaction(models.Model):
    _name = "hr.work.entry"

    name = fields.Char("Name", required=1, default="/")
    from_date = fields.Date("From Date", required=1)
    to_date = fields.Date("To Date", required=1)
    work_type = fields.Many2one("hr.work.type","Work Type", required=1)
    employee_id = fields.Many2one("hr.employee","Employee", domain=[], required=1)
    qty = fields.Float("Qty", digits=(16,2))
    uom_id = fields.Many2one("hr.work.uom", related="work_type.uom_id", string="UoM")
    price_unit = fields.Float("Price Unit",related="work_type.price_unit", store=True, digits=(16,2))
    price_total = fields.Float("Price Total", digits=(16,2))

    @api.onchange('qty')
    def onchange_qty(self):
        self.price_total = round(self.price_unit * self.qty,2)

WorkEntriesTransaction