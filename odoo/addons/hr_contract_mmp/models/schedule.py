from odoo import fields, models, api
from odoo.exceptions import UserError

class HrContractSchedule(models.Model):
    _name = "hr.contract.schedule"

    @api.constrains('date_from','date_to')
    def _check_date(self):
        for line in self:
            if line.date_from > line.date_to:
                raise UserError("Date From Greather Than Date To")
            else:
                overlap = self.search([('contract_id', '=', line.contract_id.id),('id','!=', line.id)
                                             , '|', '|'
                                         , '&',('date_from', '<=', line.date_to),   ('date_to', '>=', line.date_to)
                                         , '&',('date_from', '>=', line.date_from),('date_to', '<=', line.date_to)
                                         , '&',('date_from', '<=', line.date_from),('date_to', '>=', line.date_from)
                                          ])

                if overlap:
                    warning = list(map(lambda x: "Overlap Employee %s from %s - %s" % (
                    str(x.employee_id.name), x.date_from.strftime("%Y-%m-%d"), x.date_to.strftime("%Y-%m-%d")),
                                       overlap))
                    listToStr = ', \n'.join([str(elem) for elem in warning])
                    raise UserError(listToStr)

    date_from = fields.Date("Date From", required=1)
    date_to = fields.Date("Date To", required=1)
    resource_calendar_id = fields.Many2one("resource.calendar", "Shift")
    contract_id = fields.Many2one("hr.contract", "Contract")
    employee_id = fields.Many2one("hr.employee", related="contract_id.employee_id", store=True)

HrContractSchedule