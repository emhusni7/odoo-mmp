from odoo import models, api, _, fields, exceptions

class hrEmpoyeeAttd(models.Model):
    _inherit = "hr.employee"
    _sql_constraints = [
        ('employee_pin_uniq', 'unique (pin)', """Absen Code is Unique"""),
    ]

    @api.depends('resource_calendar_id', 'hr_presence_state')
    def _compute_presence_icon(self):
        """
        This method compute the state defining the display icon in the kanban view.
        It can be overriden to add other possibilities, like time off or attendances recordings.
        """
        # working_now_list = self.filtered(lambda e: e.hr_presence_state == 'present')._get_employee_working_now()
        for employee in self:
            icon = 'presence_present'
            employee.hr_icon_display = icon

    @api.model
    def attendance_scan(self, barcode):
        """ Receive a barcode scanned from the Kiosk Mode and change the attendances of corresponding employee.
            Returns either an action or a warning.
        """
        employee = self.sudo().search([('barcode', '=', barcode)], limit=1)
        if employee:
            return employee._attendance_action('hr_attendance_mmp.hr_attendance_action_kiosk_mode_mmp')
        return {'warning': _("No employee corresponding to Badge ID '%(barcode)s.'") % {'barcode': barcode}}

    def _attendance_action_change(self):
        """ Check In/Check Out action
            Check In: create a new attendance record
            Check Out: modify check_out field of appropriate attendance record
        """
        self.ensure_one()
        type = self.env.user.type_kios
        action_date = fields.Datetime.now()

        if type == 'in':
            attendance = self.env['hr.attendance'].search([('employee_id', '=', self.id),('check_in','<=',action_date), ('check_out', '=', False)],
                                                          limit=1, order = "check_in desc")
            if attendance:
                return False

            vals = {
                'employee_id': self.id,
                'check_in': action_date,
            }
            return self.env['hr.attendance'].create(vals)
        elif type == 'out':
            attendance = self.env['hr.attendance'].search([('employee_id', '=', self.id), ('check_out', '=', False)], limit=1)
            if attendance:
                attendance.check_out = action_date
            else:
                return False
            return attendance
        return {'warning': _("Tipe Kios Belum Di isi")}

    def _attendance_action(self, next_action):
        """ Changes the attendance of the employee.
            Returns an action to the check in/out message,
            next_action defines which menu the check in/out message should return to. ("My Attendances" or "Kiosk Mode")
        """
        self.ensure_one()
        employee = self.sudo()
        action_message = self.env["ir.actions.actions"]._for_xml_id("hr_attendance.hr_attendance_action_greeting_message")
        action_message['previous_attendance_change_date'] = employee.last_attendance_id and (employee.last_attendance_id.check_out or employee.last_attendance_id.check_in) or False
        action_message['employee_name'] = employee.name
        action_message['barcode'] = employee.barcode
        action_message['next_action'] = next_action
        action_message['hours_today'] = employee.hours_today
        modified_attendance = employee._attendance_action_change()
        if not modified_attendance and self.env.user.type_kios == 'out':
           return {'info': _("Anda Telah Check Out/ Belum Check In.'")}
        elif not modified_attendance and self.env.user.type_kios == 'in':
            return {'info': _("Anda Telah Check In.'")}
        elif isinstance(modified_attendance, dict) and 'warning' in modified_attendance.keys():
            return modified_attendance
        action_message['attendance'] = modified_attendance.read()[0]
        action_message['total_overtime'] = employee.total_overtime
        return {'action': action_message}

    #compute presence state
    #todo: check attendance checkin today jika ada maka present jika tidak
    @api.depends('user_id.im_status', 'attendance_state')
    def _compute_presence_state(self):
        """
        Override to include checkin/checkout in the presence state
        Attendance has the second highest priority after login
        """
        for employee in self:
            if not employee.last_attendance_id:
                employee.hr_presence_state = 'to_define'
            elif employee.last_attendance_id.check_in.date() == fields.Date.context_today(self):
                employee.hr_presence_state = 'present'
            else:
                employee.hr_presence_state = 'absent'