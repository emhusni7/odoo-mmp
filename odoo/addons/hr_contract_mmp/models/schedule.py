from odoo import fields, models, api
from odoo.exceptions import UserError

class HrContractSchedule(models.Model):
    _name = "hr.contract.schedule"

    @api.constrains('date_from','date_to')
    def _check_date(self):
        if self.date_from > self.date_to:
            raise UserError("Date From Greather Than Date To")

    date_from = fields.Date("Date From", required=1)
    date_to = fields.Date("Date To", required=1)
    resource_calendar_id = fields.Many2one("resource.calendar", "Shift")
    contract_id = fields.Many2one("hr.contract", "Contract")
    employee_id = fields.Many2one("hr.employee", related="contract_id.employee_id", store=True)

HrContractSchedule