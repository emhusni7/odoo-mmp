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

    def action_view_allocation(self):
        action = self.env['ir.actions.act_window']._for_xml_id('hr_holidays.hr_leave_allocation_action_my')
        action['view_mode'] = 'tree,form'
        action['domain'] = [('id', 'in', self.linked_request_ids.ids)]
        return action

    def _prepare_holiday_values(self, employees):
        self.ensure_one()
        return [{
            'name': self.name,
            'holiday_type': 'employee',
            'holiday_status_id': self.holiday_status_id.id,
            'notes': self.notes,
            'department_id': self.department_id.id,
            'number_of_days': self.number_of_days,
            'parent_id': self.id,
            'employee_id': employee.id,
            'employee_ids': [(6, 0, [employee.id])],
            'state': 'confirm',
            'allocation_type': self.allocation_type,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'accrual_plan_id': self.accrual_plan_id.id,
        } for employee in employees]

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
