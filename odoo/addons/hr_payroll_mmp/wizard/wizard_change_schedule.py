from odoo import models, fields, api

class ChangeSchedule(models.TransientModel):
    _name = 'wizard.change.schedule'

    department_id = fields.Many2one("hr.department", "Department", required=1)
    section_id = fields.Many2one("hr.job","Section", domain=[("department_id","=",department_id)])
    employee_ids = fields.Many2many("hr.employee","wiz_schedule_emp_rel","wiz_id","employee_id","Employee", domain=[("contract_id.state","=","open")])

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

    date_from = fields.Date("Date From", required=1)
    date_to = fields.Date("Date To", required=1)
    resource_calendar_id = fields.Many2one("resource.calendar","Calendar")
