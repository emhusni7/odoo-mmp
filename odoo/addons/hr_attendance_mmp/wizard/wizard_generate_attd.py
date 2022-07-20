from odoo import fields, models

class Attd(models.TransientModel):
    _name = "wiz.generate.attd"

    def generate_attd(self):

        sql = '''
           select 
                ham.id,
                ham.code,
                ham.type,
                he.id employee_id,
                ham.dtime
            from hr_attendance_mmp ham
                inner join hr_employee he ON ham."name"  = he.pin 
                where ham.has_attd is null and (ham.dtime + interval '7 hours')::Date between %s::Date and %s::Date 
            order by 
                he.id,
                ham.dtime
        '''
        self.env.cr.execute(sql,(self.date_from, self.date_to))
        # Note 1 == Check In
        # 0 == Check Out
        employee_id = False
        data = False
        attendanceObj = self.env['hr.attendance']
        mmpObj = self.env['hr.attendance.mmp']
        to_update = []
        for record in self.env.cr.dictfetchall():
            type = eval(record.get('type'))
            if employee_id != record.get('employee_id'):
                if type == 1:
                    data = {
                        'employee_id': record.get('employee_id'),
                        'check_in': record.get('dtime'),
                        'to_update': [record.get('id')]
                    }
                else:
                    continue
                employee_id = record.get('employee_id')
            else:
                #cek attendance update to attendance
                if not data and type == 1:
                    data = {
                        'employee_id': record.get('employee_id'),
                        'check_in': record.get('dtime'),
                        'to_update': [record.get('id')]
                    }
                elif type == 1 and data:
                    data['check_in'] = max(data['check_in'], record.get('dtime'))
                    data['to_update'] += [record.get('id')]
                elif type == 0 and data:
                    data['check_out'] = record.get('dtime')
                    data['to_update'] += [record.get('id')]
                    to_update = data['to_update']
                    del data['to_update']
                    attd = attendanceObj.create(data)
                    mmpObj.browse(to_update).write({'has_attd': attd.id})
                    data = False


    date_from = fields.Date("Date From", required=1)
    date_to = fields.Date("Date To", required=1)

Attd
