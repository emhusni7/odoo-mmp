from odoo import fields, models, _, api, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError

class HrLeaves(models.Model):
    _inherit = "hr.leave"

    name = fields.Char('Description', compute=False, inverse= False, search= False)
    manager_id = fields.Many2one('hr.employee', compute='_compute_from_employee_id', store=True, readonly=False)
    department_id = fields.Many2one(
        'hr.department', compute=False, store=True, string='Department', readonly=False, required=1,
        states={'cancel': [('readonly', True)], 'refuse': [('readonly', True)], 'validate1': [('readonly', True)],
                'validate': [('readonly', True)]})
    # leave type configuration
    holiday_status_id = fields.Many2one(
        "hr.leave.type",  store=True, string="Time Off Type", required=True,
        readonly=False,
        states={'cancel': [('readonly', True)], 'refuse': [('readonly', True)], 'validate1': [('readonly', True)],
                'validate': [('readonly', True)]},
        domain=['|', ('requires_allocation', '=', 'no'), ('has_valid_allocation', '=', True)])

    employee_company_id = fields.Many2one(related='employee_ids.company_id', readonly=True, store=True)
    active_employee = fields.Boolean(related='employee_ids.active', readonly=True)




    @api.depends('employee_id')
    def _compute_from_employee_id(self):
        for holiday in self:
            holiday.manager_id = holiday.employee_id.parent_id.ids

    @api.depends('employee_id', 'holiday_type')
    def _compute_department_id(self):
        for holiday in self:
            holiday.department_id = holiday.employee_id.department_id


    @api.ondelete(at_uninstall=False)
    def _unlink_if_correct_states(self):
        error_message = _('You cannot delete a time off which is in %s state')
        state_description_values = {elem[0]: elem[1] for elem in self._fields['state']._description_selection(self.env)}
        now = fields.Datetime.now()

        if not self.user_has_groups('hr_holidays.group_hr_holidays_user'):
            if any(hol.state not in ['draft', 'confirm'] for hol in self):
                raise UserError(error_message % state_description_values.get(self[:1].state))
            if any(hol.date_from < now for hol in self) and self.env.user.id not in [ emp.user_id.id for emp in self.employee_ids]:
                raise UserError(_('You cannot delete a time off which is in the past'))
        else:
            for holiday in self.filtered(lambda holiday: holiday.state not in ['draft', 'cancel', 'confirm']):
                raise UserError(error_message % (state_description_values.get(holiday.state),))

    @api.depends('holiday_type')
    def _compute_from_holiday_type(self):
        for holiday in self:
            if holiday.holiday_type == 'employee':
                holiday.mode_company_id = False
                holiday.category_id = False
            elif holiday.holiday_type == 'company':
                holiday.employee_ids = False
                if not holiday.mode_company_id:
                    holiday.mode_company_id = self.env.company.id
                holiday.category_id = False
            elif holiday.holiday_type == 'department':
                holiday.employee_ids = False
                holiday.mode_company_id = False
                holiday.category_id = False
            elif holiday.holiday_type == 'category':
                holiday.employee_ids = False
                holiday.mode_company_id = False
            else:
                holiday.employee_ids = self.env.context.get(
                    'default_employee_id') or holiday.employee_id or self.env.user.employee_id

    def activity_update(self):
        return True

    def _check_approval_update(self, state):
        """ Check if target state is achievable. """
        if self.env.is_superuser():
            return

        current_employee = self.env.user.employee_id
        is_officer = self.env.user.has_group('hr_holidays.group_hr_holidays_user')
        is_manager = self.env.user.has_group('hr_holidays.group_hr_holidays_manager')

        for holiday in self:
            val_type = holiday.validation_type

            if not is_manager and state != 'confirm':
                if state == 'draft':
                    if holiday.state == 'refuse':
                        raise UserError(_('Only a Time Off Manager can reset a refused leave.'))
                    if holiday.date_from and holiday.date_from.date() <= fields.Date.today():
                        raise UserError(_('Only a Time Off Manager can reset a started leave.'))
                    if holiday.employee_id != current_employee:
                        raise UserError(_('Only a Time Off Manager can reset other people leaves.'))
                else:
                    if val_type == 'no_validation' and current_employee == holiday.employee_id:
                        continue
                    # use ir.rule based first access check: department, members, ... (see security.xml)
                    holiday.check_access_rule('write')

                    # This handles states validate1 validate and refuse
                    if holiday.employee_id == current_employee:
                        raise UserError(_('Only a Time Off Manager can approve/refuse its own requests.'))

                    if (state == 'validate1' and val_type == 'both') and holiday.holiday_type == 'employee':
                        #husni change change leave_manaager Can approve
                        if self.env.user != holiday.employee_id.leave_manager_id:
                            raise UserError(_('You must be either %s\'s manager or Time off Manager to approve this leave') % (holiday.employee_id.name))

                    if (state == 'validate' and val_type == 'manager') and self.env.user != holiday.employee_id.leave_manager_id:
                        raise UserError(_('You must be %s\'s Manager to approve this leave', holiday.employee_id.name))

                    if not is_officer and (state == 'validate' and val_type == 'hr') and holiday.holiday_type == 'employee':
                        raise UserError(_('You must either be a Time off Officer or Time off Manager to approve this leave'))

    @api.model_create_multi
    def create(self, vals_list):
        """ Override to avoid automatic logging of creation """
        if not self._context.get('leave_fast_create'):
            leave_types = self.env['hr.leave.type'].browse(
                [values.get('holiday_status_id') for values in vals_list if values.get('holiday_status_id')])
            mapped_validation_type = {leave_type.id: leave_type.leave_validation_type for leave_type in leave_types}

            for values in vals_list:
                employee_id = values.get('employee_id', False)
                leave_type_id = values.get('holiday_status_id')
                # Handle automatic department_id
                if not values.get('department_id'):
                    values.update({'department_id': self.env['hr.employee'].browse(employee_id).department_id.id})

                # Handle no_validation
                if mapped_validation_type[leave_type_id] == 'no_validation':
                    values.update({'state': 'confirm'})

                if 'state' not in values:
                    # To mimic the behavior of compute_state that was always triggered, as the field was readonly
                    values['state'] = 'confirm' if mapped_validation_type[leave_type_id] != 'no_validation' else 'draft'

                # Handle double validation
                if mapped_validation_type[leave_type_id] == 'both':
                    self._check_double_validation_rules(employee_id, values.get('state', False))

        holidays = super(HrLeaves, self.with_context(mail_create_nosubscribe=True)).create(vals_list)

        holidays.filtered(lambda holiday: not holiday.holiday_allocation_id).with_user(
            SUPERUSER_ID)._compute_from_holiday_status_id()

        for holiday in holidays:
            if not self._context.get('leave_fast_create'):
                # Everything that is done here must be done using sudo because we might
                # have different create and write rights
                # eg : holidays_user can create a leave request with validation_type = 'manager' for someone else
                # but they can only write on it if they are leave_manager_id
                holiday_sudo = holiday.sudo()
                holiday_sudo.add_follower(employee_id)
                if holiday.validation_type == 'manager':
                    holiday_sudo.message_subscribe(partner_ids=holiday.employee_id.leave_manager_id.partner_id.ids)
                if holiday.validation_type == 'no_validation':
                    # Automatic validation should be done in sudo, because user might not have the rights to do it by himself
                    holiday_sudo.action_validate()
                    holiday_sudo.message_subscribe(partner_ids=[holiday._get_responsible_for_approval().partner_id.id])
                    holiday_sudo.message_post(body=_("The time off has been automatically approved"),
                                              subtype_xmlid="mail.mt_comment")  # Message from OdooBot (sudo)
                elif not self._context.get('import_file'):
                    holiday_sudo.activity_update()
        return holidays

    def _prepare_employees_holiday_values(self, employees):
        self.ensure_one()
        work_days_data = employees._get_work_days_data_batch(self.date_from, self.date_to)
        return [{
            'name': self.name,
            'holiday_type': 'employee',
            'holiday_status_id': self.holiday_status_id.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'request_date_from': self.request_date_from,
            'request_date_to': self.request_date_to,
            'notes': self.notes,
            'department_id': self.department_id.id,
            'number_of_days': work_days_data[employee.id]['days'],
            'parent_id': self.id,
            'employee_id': employee.id,
            'employee_ids': employee,
            'state': 'validate',
        } for employee in employees if work_days_data[employee.id]['days']]

    def action_view_leave_child(self):
        action = self.env['ir.actions.act_window']._for_xml_id('hr_holidays.hr_leave_action_my')
        action['view_mode'] = 'tree,form'
        action['domain'] = [('id', 'in', self.linked_request_ids.ids)]
        return action

    def action_validate(self):
        current_employee = self.env.user.employee_id
        leaves = self._get_leaves_on_public_holiday()
        if leaves:
            raise ValidationError(_('The following employees are not supposed to work during that period:\n %s') % ','.join(leaves.mapped('employee_id.name')))

        if any(holiday.state not in ['confirm', 'validate1'] and holiday.validation_type != 'no_validation' for holiday in self):
            raise UserError(_('Time off request must be confirmed in order to approve it.'))

        self.write({'state': 'validate'})

        leaves_second_approver = self.env['hr.leave']
        leaves_first_approver = self.env['hr.leave']

        for leave in self:
            if leave.validation_type == 'both':
                leaves_second_approver += leave
            else:
                leaves_first_approver += leave

            if leave.holiday_type != 'employee' or\
                (leave.holiday_type == 'employee' and len(leave.employee_ids) > 1):
                if leave.holiday_type == 'employee':
                    employees = leave.employee_ids
                elif leave.holiday_type == 'category':
                    employees = leave.category_id.employee_ids
                elif leave.holiday_type == 'company':
                    employees = self.env['hr.employee'].search([('company_id', '=', leave.mode_company_id.id)])
                else:
                    employees = leave.department_id.member_ids

                conflicting_leaves = self.env['hr.leave'].with_context(
                    tracking_disable=True,
                    mail_activity_automation_skip=True,
                    leave_fast_create=True
                ).search([
                    ('date_from', '<=', leave.date_to),
                    ('date_to', '>', leave.date_from),
                    ('state', 'not in', ['cancel', 'refuse']),
                    ('holiday_type', '=', 'employee'),
                    ('employee_id', 'in', employees.ids)])

                if conflicting_leaves:
                    # YTI: More complex use cases could be managed in master
                    raise ValidationError(_('You can not have 2 time off that overlaps on the same day.'))

                    # keep track of conflicting leaves states before refusal

                values = leave._prepare_employees_holiday_values(employees)
                leaves = self.env['hr.leave'].with_context(
                    tracking_disable=True,
                    mail_activity_automation_skip=True,
                    leave_fast_create=True,
                    no_calendar_sync=True,
                    leave_skip_state_check=True,
                ).create(values)

                leaves._validate_leave_request()

        leaves_second_approver.write({'second_approver_id': current_employee.id})
        leaves_first_approver.write({'first_approver_id': current_employee.id})

        employee_requests = self.filtered(lambda hol: hol.holiday_type == 'employee')
        employee_requests._validate_leave_request()
        if not self.env.context.get('leave_fast_create'):
            employee_requests.filtered(lambda holiday: holiday.validation_type != 'no_validation').activity_update()
        return True


HrLeaves
