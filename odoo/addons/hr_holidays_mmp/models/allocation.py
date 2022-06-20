from odoo import fields, models, api,_
from odoo.exceptions import UserError

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

    def _check_approval_update(self, state):
        """ Check if target state is achievable. """
        if self.env.is_superuser():
            return
        current_employee = self.env.user.employee_id
        if not current_employee:
            return
        is_officer = self.env.user.has_group('hr_holidays.group_hr_holidays_user')
        is_manager = self.env.user.has_group('hr_holidays.group_hr_holidays_manager')
        for holiday in self:
            val_type = holiday.holiday_status_id.sudo().allocation_validation_type
            if state == 'confirm':
                continue

            if state == 'draft':
                if holiday.employee_id != current_employee and not is_manager:
                    raise UserError(_('Only a time off Manager can reset other people allocation.'))
                continue

            if not is_officer and self.env.user != holiday.employee_id.leave_manager_id and not val_type == 'no':
                raise UserError(_('Only a time off Officer/Responsible or Manager can approve or refuse time off requests.'))

            if is_officer or self.env.user == holiday.employee_id.leave_manager_id:
                # use ir.rule based first access check: department, members, ... (see security.xml)
                holiday.check_access_rule('write')

            if holiday.employee_id == current_employee and not is_manager and not val_type == 'no':
                raise UserError(_('Only a time off Manager can approve its own requests.'))

            if (state == 'validate1' and val_type == 'both') or (state == 'validate' and val_type == 'manager'):
                if self.env.user == holiday.employee_id.leave_manager_id:
                    continue

            if state == 'validate' and val_type == 'both':
                if not is_officer:
                    raise UserError(_('Only a Time off Approver can apply the second approval on allocation requests.'))


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
