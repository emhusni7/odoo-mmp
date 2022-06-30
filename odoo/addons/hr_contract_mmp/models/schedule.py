from odoo import fields, models

class HrContractSchedule(models.Model):
    _name = "hr.contract.schedule"

    date_from = fields.Date("Date From", required=1)
    date_to = fields.Date("Date To", required=1)
    resource_calendar_id = fields.Many2one("resource.calendar", "Shift")
    contract_id = fields.Many2one("hr.contract", "Contract")

HrContractSchedule