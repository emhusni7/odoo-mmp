from odoo import models, fields, api
from odoo.exceptions import UserError

class ChangeSchedule(models.TransientModel):
    _name = 'wizard.change.schedule'

    department_id = fields.Many2one("hr.department", "Department", required=1)
    section_id = fields.Many2one("hr.job","Section", domain=[("department_id","=",department_id)])
    employee_ids = fields.Many2many("hr.employee","wiz_schedule_emp_rel","wiz_id","employee_id","Employee", domain=[("contract_id.state","=","open")])
    lines = fields.One2many("wizard.change.schedule.line","chg_sch_id","Lines")

    @api.onchange('department_id','section_id')
    def change_schedule(self):
        if self.section_id:
            return {
                'employee_ids':{
                    'domain':[('section_id','=',self.section_id.id)]
                }
            }
        elif self.department_id:
            return {
                'employee_ids': {
                    'domain': [('department_id', '=', self.department_id.id)]
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
    resource_calendar_id = fields.Many2one("resource.calendar","Calendar")
    chg_sch_id = fields.Many2one("wizard.change.schedule", "Schedule", required=1)

ScheduleLine