from odoo import models, api

class VehicleReport(models.AbstractModel):
    _name = 'ptk.mmp_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.sudo().env['ptk.mmp'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': self._name,
            'docs': docs,
            'data': data,
        }

VehicleReport