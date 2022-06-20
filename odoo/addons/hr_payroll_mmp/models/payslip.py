from odoo import models, fields, api, _, tools
from datetime import datetime, timedelta, time
import babel
from pytz import utc
from odoo.addons.resource.models.resource import Intervals, datetime_to_string, string_to_datetime
ROUNDING_FACTOR = 16
from math import floor

class HrPayrollStructure(models.Model):
    _inherit = "hr.payroll.structure"
    _rec_name = "complete_name"

    @api.depends('name','resource_calendar_id')
    def _get_complete_name(self):
        for x in self:
            x.complete_name = "%s with (%s hours + rest %s)"%(x.name, str(x.resource_calendar_id.hours_per_day), str(x.resource_calendar_id.rest_hours))

    @api.depends('type')
    def get_selected_type(self):
        for x in self:
            x.code = dict(x._fields['type'].selection).get(x.type)

    complete_name = fields.Char("Complete Name", compute="_get_complete_name", stored=True)
    parent_id = fields.Many2one("hr.payroll.structure","Parent Structure Id", default=False)
    resource_calendar_id = fields.Many2one("resource.calendar","Working Schedule", required=1)
    type = fields.Selection([("monthly","Monthly"),("weekly","Weekly"),("2_weekly","2 Weekly")],"Type",default="monthly" ,required=1)
    code = fields.Char("Code", compute='get_selected_type', stored=True)


HrPayrollStructure

class HrPayslipRun(models.Model):
    _inherit = "hr.payslip.run"
    _sql_constraints = [
        ('hr_payroll_structure_uniq', 'unique (name)', """Payroll Name Must Be Unique"""),
    ]

    @api.depends('department_id', 'month', 'structure_id')
    def get_payroll_name(self):
        self.name = "Payroll %s %s (%s)"%(self.department_id.name or "",
                                             dict(self._fields['month'].selection).get(self.month),
                                             dict(self.structure_id._fields['type'].selection).get(self.structure_id.type) or ""
                                             )
    @api.onchange('date_start')
    def get_month(self):
        self.month = self.date_start.strftime("%m")

    @api.onchange('date_start','date_end')
    def _get_normal_wd(self):
        start = self.date_start
        end = self.date_end
        date_generated = [start + timedelta(days=x) for x in range(0, (end - start).days)]
        self.normal_working_days = sum([1 for date in date_generated if date.weekday() < 5])

    name = fields.Char("Name", default="/", compute='get_payroll_name', store=True)
    department_id = fields.Many2one("hr.department","Department", required=1)
    divisi_id = fields.Many2one("hr.divisi.mmp",  "Divisi", domain="[('department_id','=',department_id)]")
    section_id = fields.Many2one("hr.job", "Section", domain="[('divisi_id','=',divisi_id)]")
    month = fields.Selection([("01","January"),("02","February"),("03","March"),("04","April"),
                              ("05", "Mei"), ("06", "June"),("07", "July"), ("08", "August"),
                              ("09", "September"),("10", "October"),("11", "November"),("12", "December")
                              ], "Payroll For Month", required=1)
    normal_working_days = fields.Integer("Normal Working Days", required=1)
    structure_id = fields.Many2one("hr.payroll.structure", "Structure", required=1)
    type = fields.Selection(string="Type",related="structure_id.type")



HrPayslipRun

class ResourceMixin(models.AbstractModel):
    _inherit = "resource.mixin"

    def get_work_days_data(self, from_datetime, to_datetime, compute_leaves=True, calendar=None, domain=None):
        return {}

ResourceMixin

class IntervalMMP(Intervals):

    def checkHolidayRange(att_check_in, lv,date_in, date_out, rest_hours):
        delta = timedelta(days=1)
        # check date_out attendance
        leaves = []
        date_leaves = []
        # fix looping todo
        while date_in <= date_out:
            date_leaves.append(date_in)
            date_in += delta

        for item in date_leaves:
            if item not in att_check_in.keys():
                to = datetime.combine(item, lv.holiday_id.date_to.time())
                fr = datetime.combine(item, lv.holiday_id.date_from.time())
                leaves.append({
                    'rc': lv,
                    'start': item,
                    'end': item,
                    'days': 1,
                    'hours': round((to - fr).seconds/3600,2) - rest_hours
                })

        return leaves


    def _check_onAttOverLeaveDays(self, overtime, leave, normal_worked_hours, rest_hours):
        leaves, overtimes, temp_overtime, temp_leave_hours = [], [], {}, {}
        attd_date = {}
        for at_in, at_out , att in sorted(self._items, key=lambda x:x[0]):
            if at_in.date() not in attd_date.keys():
                attd_date[at_in.date()] = {
                    'hours': att.worked_hours,
                    'data': [(at_in, at_out, att)]
                }
            else:
                attd_date[at_in.date()]['data'].append((at_in, at_out, att))
                attd_date[at_in.date()]['hours'] += att.worked_hours

            #check possibility overtime
            if floor(attd_date[at_in.date()]['hours'] - rest_hours) > normal_worked_hours:
                temp_overtime[at_in.date()] = (attd_date[at_in.date()]['data'])
            #check posibility leave hours
            if floor(attd_date[at_in.date()]['hours'] - rest_hours) < normal_worked_hours:
                leave_hours = normal_worked_hours - (attd_date[at_in.date()]['hours'] - rest_hours)
                temp_leave_hours[at_in.date()] = leave_hours

        #Cek Overtime Attendance
        #variable to remove attendance
        to_remove_attd = []
        for ov_start, ov_stop, ov in overtime._items:
            # Jika Overtime Bulk
            if ov.overtime_bulk_id.duration_type == 'days':
                #Cek tanggal overtime ada di attendance
                if attd_date.get(ov_start.date()):
                    # del self._items[idx]

                    data = attd_date.get(ov_start.date())[0]
                    start = max(data[0], ov_start)
                    end = min(data[1], ov_stop)
                    overtimes.append({
                        'ov': ov,
                        'start': start,
                        'end': end,
                        'type': 'days',
                        'hours': round((end - start).seconds()/3600,2)
                    })
                    attd_date.pop(ov_start.date(),None)
            elif ov.overtime_bulk_id.duration_type == 'hours':
                #Cek tanggal overtime di attendance
                if attd_date.get(ov_start.date()) and temp_overtime[ov_start.date()]:
                    data = temp_overtime[ov_start.date()][0]
                    start = max(data[0], ov_start)
                    end = min(data[1], ov_stop)
                    overtimes.append({
                        'ov': ov,
                        'start': start,
                        'end': end,
                        'type': 'hours',
                        'hours': round((end - start).seconds()/3600,2)
                    })

        # Leaves Computed
        for lv_in, lv_out, lv in leave._items:
            date_in, date_out = lv_in.date(), lv_out.date()
            if lv.holiday_id:
                if lv.holiday_id.holiday_status_id.request_unit == 'day':
                    newleaves = IntervalMMP.checkHolidayRange(attd_date, lv, date_in, date_out, rest_hours)
                    leaves += newleaves
                else:
                    #cek attendance di leave
                    if temp_leave_hours.get(date_in):
                        leaves.append({
                            'rc': lv,
                            'start': lv_in,
                            'end': lv_out,
                            'days': 0,
                            'hours': temp_leave_hours[date_in]
                        })
                        temp_leave_hours.pop(date_in, None)
            else:
                delta = timedelta(days=1)
                lvs = []
                #looping date out
                while date_in <= date_out:
                    #check date_in attendance
                    lvs.append(date_in)
                    to = datetime.combine(date_in, lv.date_to.time())
                    fr = datetime.combine(date_in, lv.date_from.time())
                    leaves.append({
                        'rc': lv,
                        'start': date_in,
                        'end': date_in,
                        'days': 1,
                        'hours': round((to-fr).seconds/3600 ,2)- rest_hours,
                    })
                    date_in += delta

                for toff in lvs:
                    if toff in attd_date.keys():
                        to_remove_attd.append(toff)
                        attd_date.pop(toff, None)


        result = {
            'overtime': overtimes,
            'attd': attd_date,
            'leave': leaves,
            'late': temp_leave_hours
        }
        return result

    def _check_leaveAtt(self, leave ):
        for idx, x in enumerate(self._items):
            for y in leave._items:
                if x[0].date() == y[0].date():
                    del self._items[idx]
IntervalMMP

class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    def _get_normal_wd(self, date_from, date_to):
        start = date_from or self.date_from
        end = date_to or self.date_to
        date_generated = [start + timedelta(days=x) for x in range(0, (end - start).days)]
        return sum([1 for date in date_generated if date.weekday() < 5])

    @api.depends('input_line_ids')
    def getOvertimeId(self):
        for x in self:
            over = []
            for y in x.input_line_ids:
                if y.overtime_ids.ids:
                    over.extend(y.overtime_ids.ids)
            if over:
                x.overtime_ids = over
            else:
                x.overtime_ids = False

    overtime_ids = fields.One2many("hr.overtime", compute="getOvertimeId")

    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        """
        @param contract: Browse record of contracts
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """
        res = []
        # fill only if the contract as a working schedule linked
        contract = contracts.filtered(lambda x: x.resource_calendar_id)[0]

        run_id = False
        if self._context.get('active_model') == 'hr.payslip.run':
            run_id = self.env[self._context.get('active_model')].browse(self._context.get('active_id'))
            struct_id = run_id.structure_id
        else:
            struct_id = self.struct_id
        # compute leave days
        calendar = run_id and run_id.structure_id.resource_calendar_id or contracts.resource_calendar_id
        domain = [('employee_id', '=', self.employee_id.id)]
        day_from = datetime.combine(fields.Date.from_string(date_from), time.min)
        day_to = datetime.combine(fields.Date.from_string(date_to), time.max)
        # compute worked days

        work_data = {
            'days': run_id and run_id.normal_working_days or self._get_normal_wd(date_from, date_to),
            'hours': (run_id and run_id.normal_working_days  or self._get_normal_wd(date_from, date_to)) * struct_id.resource_calendar_id.hours_per_day,
        }
        attendances = {
            'name': _("Normal Working Days paid at 100%"),
            'sequence': 1,
            'code': 'WORK100',
            'number_of_days': work_data['days'],
            'number_of_hours': work_data['hours'],
            'contract_id': contract.id,
        }
        overInterval = calendar._overtime_intervals_batch(day_from, day_to, domain=domain)
        day_leave_intervals = calendar._leave_intervals_batch(day_from.replace(tzinfo=utc), day_to.replace(tzinfo=utc), contract.employee_id.resource_id, domain=[])
        attdInterval = calendar._attendance_intervals_batch(day_from, day_to, domain=domain)

        workedHours = 0.0
        workedDays = 0.0
        number_hours = run_id and run_id.structure_id.resource_calendar_id.hours_per_day or contracts.resource_calendar_id.hours_per_day
        rest_hours = run_id and run_id.structure_id.resource_calendar_id.rest_hours or contracts.resource_calendar_id.rest_hours
        results = IntervalMMP._check_onAttOverLeaveDays(attdInterval, overInterval, day_leave_intervals, number_hours, rest_hours)
        datas = results.get('attd')
        for key in datas.keys():
            data = datas[key]
            minWorkHour = min(data.get('hours'), number_hours)
            workedDays += 1
            workedHours += minWorkHour

        data_late = results.get('late')
        lateHours = 0.0
        if data_late:
            for key in data_late.keys():
                #Hasil Late Hours dari normal working time - attendance hour
                lateHours += number_hours - datas[key].get('hours')
            if lateHours > 0:
                res.append({
                    'name': _("Late"),
                    'sequence': 9,
                    'code': 'LATE',
                    'number_of_days': 0,
                    'number_of_hours': lateHours,
                    'contract_id': contracts.id,
                })

        if workedHours > 0:
            absent = {
                'name': _("Attendance"),
                'sequence': 2,
                'code': 'ATTD',
                'number_of_days': workedDays,
                'number_of_hours': workedHours,
                'contract_id': contracts.id,
            }
            res.append(absent)
            # cek Holiday Jika hours kurang dari normal working time

            leaves = {}
            leaveHours = 0
            leaveDays = 0
            for leave in results['leave']:
                holiday = leave['rc'].holiday_id
                current_leave_struct = leaves.setdefault(holiday.holiday_status_id, {
                    'name': holiday.holiday_status_id.name or _('Global Leaves'),
                    'sequence': 5,
                    'code': holiday.holiday_status_id.code or 'GLOBAL',
                    'number_of_days': leave['days'],
                    'number_of_hours': leave['hours'],
                    'contract_id': contract.id,
                })
                leaveHours += leave['hours']
                leaveDays += leave['days']
        alpha_days = work_data['days'] - (workedDays + leaveDays)
        alpha_hours = work_data['hours'] - (workedHours + leaveHours)
        if alpha_days > 0 or alpha_hours > 0:
            alpha = {
                'name': 'Alpha',
                'sequence': 10,
                'code': 'ALPHA',
                'number_of_days': work_data['days'] - (workedDays + leaveDays),
                'number_of_hours': work_data['hours'] - (workedHours + leaveHours + lateHours),
                'contract_id': contract.id,
            }
            res.append(alpha)
        res.append(attendances)
        res.extend(leaves.values())
        return res

    @api.model
    def get_inputs(self, contracts, date_from, date_to):
        """
        function used for writing overtime record in payslip
        input tree.

        """
        res = super(HrPayslip, self).get_inputs(contracts, date_to, date_from)
        overtime_type = self.env.ref('hr_overtime_mmp.hr_salary_rule_overtime')
        overtime_id = self.env['hr.overtime'].search([('employee_id', '=', contracts.employee_id.id),
                                                      ('overtime_bulk_id.state', '=', 'approved'),
                                                      ('date_from','>=',date_from),
                                                      ('date_to','<=',date_to)
                                                      ])
        hrs_amount = overtime_id.mapped('cash_hrs_amount')
        day_amount = overtime_id.mapped('cash_day_amount')
        cash_amount = sum(hrs_amount) + sum(day_amount)
        if overtime_id:
            input_data = {
                'name': overtime_type.name,
                'code': overtime_type.code,
                'amount': cash_amount,
                'contract_id': contracts.id,
                'overtime_ids': [(6,0,overtime_id.ids)]
            }
            res.append(input_data)
        return res

    def onchange_employee_id(self, date_from, date_to, employee_id=False, contract_id=False):

        # defaults
        res = {
            'value': {
                'line_ids': [],
                # delete old input lines
                'input_line_ids': [(2, x,) for x in self.input_line_ids.ids],
                # delete old worked days lines
                'worked_days_line_ids': [(2, x,) for x in self.worked_days_line_ids.ids],
                # 'details_by_salary_head':[], TODO put me back
                'name': '',
                'contract_id': False,
                'struct_id': False,
            }
        }
        if (not employee_id) or (not date_from) or (not date_to):
            return res
        ttyme = datetime.combine(fields.Date.from_string(date_from), time.min)
        employee = self.env['hr.employee'].browse(employee_id)
        locale = self.env.context.get('lang') or 'en_US'
        res['value'].update({
            'name': _('Salary Slip of %s for %s') % (
            employee.name, tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale))),
            'company_id': employee.company_id.id,
        })

        if not self.env.context.get('contract'):
            # fill with the first contract of the employee
            contract_ids = self.get_contract(employee, date_from, date_to)
        else:
            if contract_id:
                # set the list of contract for which the input have to be filled
                contract_ids = [contract_id]
            else:
                # if we don't give the contract, then the input to fill should be for all current contracts of the employee
                contract_ids = self.get_contract(employee, date_from, date_to)

        if not contract_ids:
            return res
        contract = self.env['hr.contract'].browse(contract_ids[0])
        res['value'].update({
            'contract_id': contract.id
        })
        struct = contract.struct_id
        if not struct:
            return res
        res['value'].update({
            'struct_id': struct.id,
        })
        # computation of the salary input
        contracts = self.env['hr.contract'].browse(contract_ids)
        worked_days_line_ids = self.get_worked_day_lines(contracts, date_from, date_to)
        input_line_ids = self.get_inputs(contracts, date_from, date_to)
        res['value'].update({
            'worked_days_line_ids': worked_days_line_ids,
            'input_line_ids': input_line_ids,
        })
        return res

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):

        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            return

        employee = self.employee_id
        date_from = self.date_from
        date_to = self.date_to
        contract_ids = []

        ttyme = datetime.combine(fields.Date.from_string(date_from), time.min)
        locale = self.env.context.get('lang') or 'en_US'
        self.name = _('Salary Slip of %s for %s') % (
        employee.name, tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale)))
        self.company_id = employee.company_id

        if not self.env.context.get('contract') or not self.contract_id:
            contract_ids = self.get_contract(employee, date_from, date_to)
            if not contract_ids:
                return
            self.contract_id = self.env['hr.contract'].browse(contract_ids[0])

        if not self.contract_id.struct_id:
            return
        self.struct_id = self.contract_id.struct_id
        if self.contract_id:
            contract_ids = self.contract_id.ids
        # computation of the salary input
        contracts = self.env['hr.contract'].browse(contract_ids)
        worked_days_line_ids = self.get_worked_day_lines(contracts, date_from, date_to)
        worked_days_lines = self.worked_days_line_ids.browse([])
        for r in worked_days_line_ids:
            worked_days_lines += worked_days_lines.new(r)
        self.worked_days_line_ids = worked_days_lines

        input_line_ids = self.get_inputs(contracts, date_from, date_to)
        input_lines = self.input_line_ids.browse([])
        for r in input_line_ids:
            input_lines += input_lines.new(r)
        self.input_line_ids = input_lines
        return

HrPayslip


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    @api.model
    def _get_domain(self):
        active_id = self._context.get("active_id")
        runObj = self.env['hr.payslip.run'].browse(active_id)
        domain = [('contract_id.struct_id','=',runObj.structure_id.id)]
        if runObj.section_id:
            return [('job_id','=', runObj.section_id.id),('active','=',True)]
        elif runObj.divisi_id:
            return [('divisi_id', '=', runObj.divisi_id.id),('active','=',True)]
        elif runObj.department_id:
            return [('department_id', '=', runObj.department_id.id),('active','=',True)]
        else:
            return domain

    employee_ids = fields.Many2many('hr.employee', 'hr_employee_group_rel', 'payslip_id', 'employee_id', 'Employees', domain=_get_domain)

HrPayslipEmployees