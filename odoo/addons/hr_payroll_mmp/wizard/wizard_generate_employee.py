from odoo import api, fields, models, _
from odoo.exceptions import UserError

class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    def compute_sheet(self):
        run_id = self._context.get("active_id")
        run_obj = self.env["hr.payslip.run"]
        if run_id:
           payslip_run = run_obj.browse(run_id)
           slips = payslip_run.slip_ids.filtered(lambda x: x.employee_id.id in self.employee_ids.ids)
           slips.unlink()
        return super(HrPayslipEmployees, self).compute_sheet()

HrPayslipEmployees