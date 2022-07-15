from odoo import models, fields, api

class WizPayroll(models.TransientModel):
    _name = "wiz.payroll.report"

    @api.model
    def year_selection(self):
        year = fields.Date.context_today(self).year - 4  # replace 2000 with your a start year
        year_list = []
        while year <= fields.Date.context_today(self).year:  # replace 2030 with your end year
            year_list.append((str(year), str(year)))
            year += 1
        return year_list

    month = fields.Selection([("01","January"),("02","February"),("03","March"),("04","April"),
                              ("05", "Mei"), ("06", "June"),("07", "July"), ("08", "August"),
                              ("09", "September"),("10", "October"),("11", "November"),("12", "December")
                              ], "Month", required=1, default= lambda x: str(fields.Date.context_today(x).month).zfill(2))
    struct_id = fields.Many2one("hr.payroll.structure", "Struct", required=1)
    year = fields.Selection(
        year_selection,
        string="Year",
        required=1,
        default= lambda x: str(fields.Date.context_today(x).year),  # as a default value it would be 2019
    )

    def print_report(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/hr_payroll_mmp/report_payroll/%s' % (self.id),
            'target': 'new',
        }

