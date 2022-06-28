from odoo import models, fields, api, _, tools
from odoo.exceptions import UserError
from datetime import datetime, timedelta, time
import babel
from pytz import utc
from odoo.addons.resource.models.resource import Intervals, datetime_to_string, string_to_datetime
ROUNDING_FACTOR = 16
from math import floor

class PayslipInput(models.Model):
    _inherit = "hr.payslip.input"

    overtime_ids = fields.One2many("hr.overtime","input_id","Overtime")

PayslipInput

class HrPayrollStructure(models.Model):
    _inherit = "hr.payroll.structure"
    _rec_name = "complete_name"

    @api.depends('name')
    def _get_complete_name(self):
        for x in self:
            x.complete_name = "%s"%(x.name)

    @api.depends('type')
    def get_selected_type(self):
        for x in self:
            x.code = dict(x._fields['type'].selection).get(x.type)

    complete_name = fields.Char("Complete Name", compute="_get_complete_name", stored=True)
    parent_id = fields.Many2one("hr.payroll.structure","Parent Structure Id", default=False)
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


    name = fields.Char("Name", default="/", compute='get_payroll_name', store=True)
    department_id = fields.Many2one("hr.department","Department", required=1)
    divisi_id = fields.Many2one("hr.divisi.mmp",  "Divisi", domain="[('department_id','=',department_id)]")
    section_id = fields.Many2one("hr.job", "Section", domain="[('divisi_id','=',divisi_id)]")
    month = fields.Selection([("01","January"),("02","February"),("03","March"),("04","April"),
                              ("05", "Mei"), ("06", "June"),("07", "July"), ("08", "August"),
                              ("09", "September"),("10", "October"),("11", "November"),("12", "December")
                              ], "Payroll For Month", required=1)
    structure_id = fields.Many2one("hr.payroll.structure", "Structure", required=1)
    type = fields.Selection(string="Type",related="structure_id.type")

    def unlink(self):
        for run in self:
            run.slip_ids.unlink()
        return super(HrPayslipRun, self).unlink()

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


    def _check_onAttOverLeaveDays(self, overtime, leave, rest_hours, attd):
        leaves, overtimes, temp_overtime, temp_leave_hours = [], [], {}, {}
        attd_date = {}
        for at_in, at_out , att in sorted(self._items, key=lambda x:x[0]):
            dow = str(at_in.date().weekday())
            if at_in.date() not in attd_date.keys():
                attd_date[at_in.date()] = {
                    'hours': att.worked_hours - rest_hours,
                    'data': [(at_in, at_out, att)]
                }
            else:
                attd_date[at_in.date()]['data'].append((at_in, at_out, att))
                attd_date[at_in.date()]['hours'] += att.worked_hours -rest_hours

            #check possibility overtime
            if floor(attd_date[at_in.date()]['hours']) > (attd[dow] or 0):
                temp_overtime[at_in.date()] = (attd_date[at_in.date()]['data'])

            #check posibility leave hours
            if floor(attd_date[at_in.date()]['hours']) < (attd[dow] or 0):
                leave_hours = attd[dow] - (attd_date[at_in.date()]['hours'] - rest_hours)
                temp_leave_hours[at_in.date()] = leave_hours

        #Cek Overtime Attendance
        #variable to remove attendance
        to_remove_attd = []
        for ov_start, ov_stop, ov in overtime._items:
            # Jika Overtime Bulk
            dow = str(at_in.date().weekday())
            if ov.overtime_bulk_id.ov_type.duration_type == 'days':
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
                        'hours': round((end - start).seconds/3600,2),
                        'amount': ov.cash_day_amount
                    })
                    attd_date.pop(ov_start.date(),None)
            elif ov.overtime_bulk_id.ov_type.duration_type == 'hours':
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
                        'hours': round((end - start).seconds/3600,2),
                        'amount': ov.cash_hrs_amount
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

    @api.model
    def _get_payslip_lines(self, contract_ids, payslip_id):

        def _sum_salary_rule_category(localdict, category, amount):
            if category.parent_id:
                localdict = _sum_salary_rule_category(localdict, category.parent_id, amount)
            localdict['categories'].dict[category.code] = category.code in localdict['categories'].dict and \
                                                          localdict['categories'].dict[category.code] + amount or amount
            return localdict

        class BrowsableObject(object):
            def __init__(self, employee_id, dict, env):
                self.employee_id = employee_id
                self.dict = dict
                self.env = env

            def __getattr__(self, attr):
                return attr in self.dict and self.dict.__getitem__(attr) or 0.0

        class InputLine(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""

            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute("""
                        SELECT sum(amount) as sum
                        FROM hr_payslip as hp, hr_payslip_input as pi
                        WHERE hp.employee_id = %s AND hp.state = 'done'
                        AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s""",
                                    (self.employee_id, from_date, to_date, code))
                return self.env.cr.fetchone()[0] or 0.0

        class WorkedDays(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""

            def _sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute("""
                        SELECT sum(number_of_days) as number_of_days, sum(number_of_hours) as number_of_hours
                        FROM hr_payslip as hp, hr_payslip_worked_days as pi
                        WHERE hp.employee_id = %s AND hp.state = 'done'
                        AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s""",
                                    (self.employee_id, from_date, to_date, code))
                return self.env.cr.fetchone()

            def sum(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res and res[0] or 0.0

            def sum_hours(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res and res[1] or 0.0

        class Payslips(BrowsableObject):
            """a class that will be used into the python code, mainly for usability purposes"""

            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = fields.Date.today()
                self.env.cr.execute("""SELECT sum(case when hp.credit_note = False then (pl.total) else (-pl.total) end)
                                FROM hr_payslip as hp, hr_payslip_line as pl
                                WHERE hp.employee_id = %s AND hp.state = 'done'
                                AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pl.slip_id AND pl.code = %s""",
                                    (self.employee_id, from_date, to_date, code))
                res = self.env.cr.fetchone()
                return res and res[0] or 0.0

        class WorkEntry(BrowsableObject):
            def sum(self, from_date, to_date):
                self.env.cr.execute("""
                    SELECT sum(price_total)
                        FROM hr_work_entry where employee_id = %s and from_date between %s and %s 
                """, (self.employee_id, from_date, to_date))
                res = self.env.cr.fetchone()
                return res and res[0] or 0.0

        # we keep a dict with the result because a value can be overwritten by another rule with the same code
        result_dict = {}
        rules_dict = {}
        worked_days_dict = {}
        inputs_dict = {}
        blacklist = []
        payslip = self.env['hr.payslip'].browse(payslip_id)
        for worked_days_line in payslip.worked_days_line_ids:
            worked_days_dict[worked_days_line.code] = worked_days_line
        for input_line in payslip.input_line_ids:
            inputs_dict[input_line.code] = input_line

        categories = BrowsableObject(payslip.employee_id.id, {}, self.env)
        inputs = InputLine(payslip.employee_id.id, inputs_dict, self.env)
        worked_days = WorkedDays(payslip.employee_id.id, worked_days_dict, self.env)
        payslips = Payslips(payslip.employee_id.id, payslip, self.env)
        rules = BrowsableObject(payslip.employee_id.id, rules_dict, self.env)
        work_entries = WorkEntry(payslip.employee_id.id, {}, self.env)

        baselocaldict = {'categories': categories, 'rules': rules, 'payslip': payslips, 'worked_days': worked_days,
                         'inputs': inputs, 'entries': work_entries}
        # get the ids of the structures on the contracts and their parent id as well
        contracts = self.env['hr.contract'].browse(contract_ids)
        if len(contracts) == 1 and payslip.struct_id:
            structure_ids = list(set(payslip.struct_id._get_parent_structure().ids))
        else:
            structure_ids = contracts.get_all_structures()
        # get the rules of the structure and thier children
        rule_ids = self.env['hr.payroll.structure'].browse(structure_ids).get_all_rules()
        # run the rules by sequence
        sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x: x[1])]
        sorted_rules = self.env['hr.salary.rule'].browse(sorted_rule_ids)

        for contract in contracts:
            employee = contract.employee_id
            localdict = dict(baselocaldict, employee=employee, contract=contract)
            for rule in sorted_rules:
                key = rule.code + '-' + str(contract.id)
                localdict['result'] = None
                localdict['result_qty'] = 1.0
                localdict['result_rate'] = 100
                # check if the rule can be applied
                if rule._satisfy_condition(localdict) and rule.id not in blacklist:
                    # compute the amount of the rule
                    amount, qty, rate = rule._compute_rule(localdict)
                    # check if there is already a rule computed with that code
                    previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                    # set/overwrite the amount computed for this rule in the localdict
                    tot_rule = amount * qty * rate / 100.0
                    localdict[rule.code] = tot_rule
                    rules_dict[rule.code] = rule
                    # sum the amount for its salary category
                    localdict = _sum_salary_rule_category(localdict, rule.category_id, tot_rule - previous_amount)
                    # create/overwrite the rule in the temporary results
                    result_dict[key] = {
                        'salary_rule_id': rule.id,
                        'contract_id': contract.id,
                        'name': rule.name,
                        'code': rule.code,
                        'category_id': rule.category_id.id,
                        'sequence': rule.sequence,
                        'appears_on_payslip': rule.appears_on_payslip,
                        'condition_select': rule.condition_select,
                        'condition_python': rule.condition_python,
                        'condition_range': rule.condition_range,
                        'condition_range_min': rule.condition_range_min,
                        'condition_range_max': rule.condition_range_max,
                        'amount_select': rule.amount_select,
                        'amount_fix': rule.amount_fix,
                        'amount_python_compute': rule.amount_python_compute,
                        'amount_percentage': rule.amount_percentage,
                        'amount_percentage_base': rule.amount_percentage_base,
                        'register_id': rule.register_id.id,
                        'amount': amount,
                        'employee_id': contract.employee_id.id,
                        'quantity': qty,
                        'rate': rate,
                    }
                else:
                    # blacklist this rule and its children
                    blacklist += [id for id, seq in rule._recursive_search_of_rules()]

        return list(result_dict.values())

    def _get_normal_wd(self, date_from, date_to, contract):

        if not contract.resource_calendar_id.attendance_ids:
            raise UserError("Contract Working Time Not Set")

        attendance = { x.dayofweek: x.work_hours for x in contract.resource_calendar_id.attendance_ids}

        start = date_from or self.date_from
        end = date_to or self.date_to
        date_generated = [start + timedelta(days=x) for x in range(0, (end - start).days)]
        res = {
            'work_days': 0,
            'work_hours': 0,
        }
        for date in date_generated:
            dow = str(date.weekday())
            if dow in attendance.keys():
                res['work_days'] += 1
                res['work_hours'] += attendance[dow]
        return res, attendance

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
        calendar =  contracts.resource_calendar_id
        domain = [('employee_id', '=', contract.employee_id.id)]
        day_from = datetime.combine(fields.Date.from_string(date_from), time.min)
        day_to = datetime.combine(fields.Date.from_string(date_to), time.max)
        # compute worked days
        day_data, attd = self._get_normal_wd(date_from, date_to, contract)
        work_data = {
            'days': day_data['work_days'],
            'hours': day_data['work_hours'],
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
        rest_hours = contracts.resource_calendar_id.rest_hours
        results = IntervalMMP._check_onAttOverLeaveDays(attdInterval, overInterval, day_leave_intervals, rest_hours, attd)
        datas = results.get('attd')
        for key in datas.keys():
            data = datas[key]
            minWorkHour = min(data.get('hours'), attd[str(data['data'][0][0].weekday())])
            workedDays += 1
            workedHours += minWorkHour

        data_late = results.get('late')
        lateHours = 0.0
        if data_late:
            for key in data_late.keys():
                #Hasil Late Hours dari normal working time - attendance hour
                lateHours += attd[str(key.weekday())] - (datas[key].get('hours'))
        # Masukkan telat ketika jumlah worked hours Kurang, dan WorkedDays == normal worked data
            if lateHours > 0 and (work_data['hours'] > workedHours):
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
        alpha_hours = work_data['hours'] - (workedHours + leaveHours + lateHours)
        if alpha_days > 0 or alpha_hours > 0:
            alpha = {
                'name': 'Alpha',
                'sequence': 10,
                'code': 'ALPHA',
                'number_of_days': alpha_days,
                'number_of_hours': alpha_hours,
                'contract_id': contract.id,
            }
            res.append(alpha)

        res.append(attendances)
        res.extend(leaves.values())
        return res, results.get('overtime')

    @api.model
    def get_inputs(self, contracts, date_from, date_to, overtime= {}):
        """
        function used for writing overtime record in payslip
        input tree.

        """
        res = super(HrPayslip, self).get_inputs(contracts, date_to, date_from)
        overtime_type = self.env.ref('hr_overtime_mmp.hr_salary_rule_overtime')
        cash_amount = 0
        overtime_ids = []
        for x in overtime:
            cash_amount += round(x.get('amount') * floor(x.get('hours')),0)
            overtime_ids.append(x.get('ov').id)

        if cash_amount:
            input_data = {
                'name': overtime_type.name,
                'code': overtime_type.code,
                'amount': cash_amount,
                'contract_id': contracts.id,
                'overtime_ids': [(6,0,overtime_ids)]
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
        worked_days_line_ids, overtimes = self.get_worked_day_lines(contracts, date_from, date_to)
        input_line_ids = self.get_inputs(contracts, date_from, date_to, overtime = overtimes)
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