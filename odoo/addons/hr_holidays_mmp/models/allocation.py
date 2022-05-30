from odoo import fields, models, api

class Allocation(models.Model):
    _inherit = "hr.leave.allocation"
    def _domain_holiday_status_id(self):
        return ['|',('requires_allocation', '=', 'yes'),('employee_requests', '=', 'yes')]

    name = fields.Char('Description', compute=False, inverse=False, compute_sudo=False)
    department_id = fields.Many2one(
        'hr.department', compute=False, string='Department',
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]})
    employee_ids = fields.Many2many('hr.employee', domain="[('department_id','=',department_id)]", compute=False, string='Employees', readonly=False,
        states={'cancel': [('readonly', True)], 'refuse': [('readonly', True)], 'validate': [('readonly', True)]})
    holiday_status_id = fields.Many2one(
        "hr.leave.type", compute=False, string="Time Off Type", required=True,
        readonly=False,
        states={'cancel': [('readonly', True)], 'refuse': [('readonly', True)], 'validate1': [('readonly', True)],
                'validate': [('readonly', True)]},
        domain=_domain_holiday_status_id,
        default=False)
    active_employee = fields.Boolean('Active Employee', related='employee_ids.active', readonly=True)

    @api.depends('holiday_type')
    def _compute_from_holiday_type(self):
        default_employee_ids = self.env['hr.employee'].browse(
            self.env.context.get('default_employee_id')) or self.env.user.employee_id
        for allocation in self:
            if allocation.holiday_type == 'employee':
                allocation.mode_company_id = False
                allocation.category_id = False
            elif allocation.holiday_type == 'company':
                allocation.employee_ids = False
                if not allocation.mode_company_id:
                    allocation.mode_company_id = self.env.company
                allocation.category_id = False
            elif allocation.holiday_type == 'department':
                allocation.employee_ids = False
                allocation.mode_company_id = False
                allocation.category_id = False
            elif allocation.holiday_type == 'category':
                allocation.employee_ids = False
                allocation.mode_company_id = False
            else:
                allocation.employee_ids = default_employee_ids
