from odoo import models, fields, api
from odoo.exceptions import UserError

class ChangeSchedule(models.TransientModel):
    _name = 'wizard.change.schedule'

    department_id = fields.Many2one("hr.department", "Department", required=1)
    section_id = fields.Many2one("hr.job","Section")
    employee_ids = fields.Many2many("hr.employee","wiz_schedule_emp_rel","wiz_id","employee_id","Employee", domain=[("contract_id.state","=","open")])
    lines = fields.One2many("wizard.change.schedule.line","chg_sch_id","Lines")

    def generate_schedule(self):
        objLine = self.sudo().env['hr.contract.schedule']
        for line in self.lines:
            # overlap dari cek apakah date_from antara date_from(sch) dan date_to(sch)
            # overlap dari cek apakah date_t0 antara date_from(sch) dan date_to(sch)
            # overlap dari cek apakah antarta date_from date_t0 ada schedule
            overlap = objLine.search([('employee_id','in', self.employee_ids.ids)
                               ,'|','|','&',('date_from','<=', line.date_to),('date_to','>=',line.date_to)
                               ,'&',('date_from','>=', line.date_from),('date_to','<=',line.date_to)
                               , '&', ('date_from', '<=', line.date_from), ('date_to', '>=', line.date_from)
                            ])
            if overlap:
               warning = list(map(lambda x: "Overlap Employee %s from %s - %s"%(str(x.employee_id.name),x.date_from.strftime("Y-%m-%d"),x.date_to.strftime("Y-%m-%d")),overlap))
               listToStr = ', \n'.join([str(elem) for elem in warning])
               raise UserError(listToStr)
            else:
                for emp in self.employee_ids:
                    emp
        return

    @api.onchange('department_id','section_id')
    def change_schedule(self):
        if self.section_id:
            return {
                'domain':{
                    'employee_ids':[('job_id','=',self.section_id.id),('contract_id.state','=','open')],

                }
            }
        elif self.department_id:
            return {
                'domain': {
                    'employee_ids': [('department_id', '=', self.department_id.id),('contract_id.state','=','open')],
                    'section_id': [('department_id','=', self.department_id.id)]
                }
            }
        else:
            return {
                'domain':{
                    'employee_ids': [('contract_id.state','=','open')],
                    'section_id': [('department_id', '=', self.department_id.id)]
                }
            }
ChangeSchedule

class ScheduleLine(models.TransientModel):
    _name = "wizard.change.schedule.line"

    @api.constrains('date_from','date_to')
    def _check_date_(self):
        if self.date_to < self.date_from:
            raise UserError("Date From Greather than Date To")


    date_from = fields.Date("Date From", required=1)
    date_to = fields.Date("Date To", required=1)
    resource_calendar_id = fields.Many2one("resource.calendar","Calendar" , required=1)
    chg_sch_id = fields.Many2one("wizard.change.schedule", "Schedule")

ScheduleLine