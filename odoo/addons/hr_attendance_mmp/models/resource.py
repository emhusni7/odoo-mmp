from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class ResourceCaledar(models.Model):
    _inherit = "resource.calendar"

    @api.constrains('attendance_ids')
    def _check_attendance(self):
        # Avoid superimpose in attendance
        sql = '''
            Select 
                rca.calendar_id,
                rca.dayofweek,
                count(*) jml
            from resource_calendar_attendance rca
                where calendar_id in %s
            group by 
                rca.calendar_id,
                rca.dayofweek 
            having(count(*) > 1)                
                '''
        self.env.cr.execute(sql,[tuple(self.ids),])
        data = self.env.cr.dictfetchall()
        if data:
            raise ValidationError("Attendance Overlap")



    attendance_ids = fields.One2many('resource.calendar.attendance', 'calendar_id', 'Working Time', readonly=False, copy=True)

ResourceCaledar

class RCAttendance(models.Model):
    _inherit = "resource.calendar.attendance"

    work_hours = fields.Float("Work Hours")
    hour_from = fields.Float(string='Work from', required=False, index=True,
                             help="Start and End time of working.\n"
                                  "A specific value of 24:00 is interpreted as 23:59:59.999999.")
    hour_to = fields.Float(string='Work to', required=False)
    day_period = fields.Selection([('morning', 'Morning'), ('afternoon', 'Afternoon')], required=False,
                                  default='morning')

    def _copy_attendance_vals(self):
        self.ensure_one()
        return {
            'name': self.name,
            'dayofweek': self.dayofweek,
            'hour_from': 0,
            'hour_to': 0,
            'day_period': self.day_period,
            'display_type': self.display_type,
            'sequence': self.sequence,
        }
RCAttendance