# -*- coding: utf-8 -*-
from dateutil import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools.safe_eval import safe_eval
import math

class ResCompany(models.Model):
    _inherit = "res.company"

    umk = fields.Monetary("UMK", currency_field="currency_id")
ResCompany

class HrOverTime(models.Model):
    _name = 'hr.overtime'
    _description = "HR Overtime"

    @api.constrains('date_from','date_to')
    def _get_constrain_date_from_to(self):
        for x in self:
            if x.overtime_bulk_id:
                if x.date_from < x.overtime_bulk_id.date_from or x.date_from > x.overtime_bulk_id.date_to:
                    raise ValidationError(_("Date from not in range"))
                elif x.date_to < x.overtime_bulk_id.date_from or x.date_to > x.overtime_bulk_id.date_to:
                    raise ValidationError(_("Date from not in range"))

    @api.onchange('date_from','date_to')
    def employee_onchange(self):
        if self.overtime_bulk_id.section_id:
            return {
                'domain': {
                    'employee_id': [('job_id', '=', self.overtime_bulk_id.section_id.id)]
                }
            }
        elif self.overtime_bulk_id.divisi_id:
            return {
                'domain': {
                    'employee_id': [('divisi_id', '=', self.overtime_bulk_id.divisi_id.id)]
                }
            }
        else:
            return {
                'domain': {
                    'employee_id': [('department_id', '=', self.overtime_bulk_id.department_id.id)]
                }
            }

    name = fields.Char('Description', readonly=False, required=1)
    employee_id = fields.Many2one('hr.employee', string='Employee',required=True)
    date_from = fields.Datetime('Date From', default= lambda self: self._context.get('date_from'), required=1)
    date_to = fields.Datetime('Date to', default=lambda self: self._context.get('date_to'), required=1)
    days_no_tmp = fields.Float('Hours', store=True)
    days_no = fields.Float('No. of Days', store=True)
    cash_hrs_amount = fields.Float(string='Overtime Amount / Hours')
    cash_day_amount = fields.Float(string='Overtime Amount / Days')
    overtime_bulk_id = fields.Many2one("hr.overtime.bulk", "Overtime Bulk")

    @api.onchange('date_from', 'date_to')
    def _get_days(self):
        for recd in self:
            if recd.date_from and recd.date_to:
                if recd.date_from > recd.date_to:
                    raise ValidationError('Start Date must be less than End Date')
        for sheet in self:
            if sheet.date_from and sheet.date_to:
                start_dt = fields.Datetime.from_string(sheet.date_from)
                finish_dt = fields.Datetime.from_string(sheet.date_to)
                s = finish_dt - start_dt
                difference = relativedelta.relativedelta(finish_dt, start_dt)
                hours = difference.hours
                minutes = difference.minutes
                days_in_mins = s.days * 24 * 60
                hours_in_mins = hours * 60
                days_no = int(math.ceil((days_in_mins + hours_in_mins + minutes) / (24 * 60)))

                diff = sheet.date_to - sheet.date_from
                days, seconds = diff.days, diff.seconds
                hours = days * 24 + seconds / 3600
                sheet.update({
                    'days_no_tmp': hours - self.overtime_bulk_id.rest_hours,
                    'days_no': days_no
                })

    def get_amount(self, xy):
        try:
            localdict = {'employee': self.employee_id, 'line': self, 'type': self.overtime_bulk_id.ov_type,
                         'company': self.env.user.sudo().company_id}
            safe_eval(xy.amount_compute, localdict, mode='exec', nocopy=True)
            return float(localdict['result'])
        except:
            raise UserError(_('Wrong python code defined %s .') % (self.employee_id.name))

    @api.onchange('days_no_tmp','days_no')
    def _get_hour_amount(self):
        ov_type = self.overtime_bulk_id.ov_type
        if ov_type.rule_line_ids and ov_type.duration_type == 'hours':
            for xy in ov_type.rule_line_ids:
                if xy.from_hrs <= self.days_no_tmp <= xy.to_hrs:
                    if xy.type == 'python_code':
                        cash_amount = self.get_amount(xy)
                        self.cash_hrs_amount = cash_amount
                    else:
                        cash_amount = xy.hrs_amount
                        self.cash_hrs_amount = cash_amount
        elif ov_type.duration_type == 'ins_h':
            for xy in ov_type.rule_line_ids:
                if xy.from_hrs <= self.days_no_tmp <= xy.to_hrs:
                    if xy.type == 'python_code':
                        cash_amount = self.get_amount(xy)
                        self.cash_hrs_amount = cash_amount
                    else:
                        cash_amount = xy.hrs_amount
                        self.cash_hrs_amount = cash_amount
        elif ov_type.duration_type == 'days':
            for xy in ov_type.rule_line_ids:
                if xy.from_hrs <= self.days_no <= xy.to_hrs:
                    if xy.type == 'python_code':
                        cash_amount = self.get_amount(xy)
                        self.cash_day_amount = cash_amount
                    else:
                        cash_amount = xy.hrs_amount
                        self.cash_day_amount = cash_amount


class HrOverTimeType(models.Model):
    _name = 'overtime.type'
    _description = "HR Overtime Type"

    name = fields.Char('Name')
    type = fields.Selection([('cash', 'Cash'),
                             ('leave', 'Time Off')])
    duration_type = fields.Selection([('hours', 'Hour'), ('days', 'Days'),('ins_h', 'Insentive (Amount)')], string="Duration Type", default="hours",
                                     required=True)
    leave_type = fields.Many2one('hr.leave.type', string='Leave Type', domain="[('id', 'in', leave_compute)]")
    leave_compute = fields.Many2many('hr.leave.type', compute="_get_leave_type")
    rule_line_ids = fields.One2many('overtime.type.rule', 'type_line_id')

    @api.onchange('duration_type')
    def _get_leave_type(self):
        ids = []
        if self.duration_type:
            if self.duration_type == 'days':
                dur = 'day'
            else:
                dur = 'hour'
            leave_type = self.env['hr.leave.type'].search([('request_unit', '=', dur)])
            for recd in leave_type:
                ids.append(recd.id)
            self.leave_compute = ids


class HrOverTimeTypeRule(models.Model):
    _name = 'overtime.type.rule'
    _description = "HR Overtime Type Rule"

    type_line_id = fields.Many2one('overtime.type', string='Over Time Type')
    name = fields.Char('Name', required=True)
    from_hrs = fields.Float('From', required=True)
    to_hrs = fields.Float('To', required=True)
    type = fields.Selection([('fix','Fix Amount'),('python_code','Python Code')],'Compute Type', default='fix', required=1)
    amount_compute = fields.Text("Python Amt Compute",
                    default='''
                        # Available variables:
                        #----------------------
                        # line: object containing overtime.type.rule
                        # company: company object
                        # employee: employee object
                        # type: overtime type object
    
                        # Note: returned value have to be set in the variable 'result'
    
                        result = rules.NET > categories.NET * 0.10'''
                    )
    hrs_amount = fields.Float('Amount', required=False)
