from odoo import models, fields

class PTKReport(models.TransientModel):
    _name = "wiz.ptk.report"

    date_from = fields.Date("From Date", default= fields.Date.today(), required=1)
    date_to = fields.Date("To Date", default= fields.Date.today(), required=1)
    stage_id = fields.Many2one("hr.recruitment.stage","Stage")

    def get_excel_report(self):
        return {
            'type': 'ir.actions.act_url',
            'url': '/hr_recruitement_mmp/excel_report/%s' % (self.id),
            'target': 'new',
        }
PTKReport
