from odoo import models, fields, api
from pytz import utc, timezone
from datetime import timedelta
from odoo.addons.resource.models.resource import Intervals, datetime_to_string, string_to_datetime
from collections import defaultdict

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def _get_unusual_days(self, date_from, date_to=None):
        return {}

HrEmployee



class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    rest_hours = fields.Float("Res Hours /Day", default=0, help="Rest Hours Per Day.")
    working_days_week = fields.Selection([("5", "5 days"), ("6", "6 days")], "Working Days a Week")

    @api.onchange('attendance_ids', 'two_weeks_calendar')
    def _onchange_hours_per_day(self):
        return False

    def _leave_intervals_batch(self, start_dt, end_dt, resources=None, domain=None, tz=None):
        """ Return the leave intervals in the given datetime range.
            The returned intervals are expressed in specified tz or in the calendar's timezone.
        """
        resources = self.env['resource.resource'] if not resources else resources
        assert start_dt.tzinfo and end_dt.tzinfo
        self.ensure_one()

        # for the computation, express all datetimes in UTC
        resources_list = list(resources) + [self.env['resource.resource']]
        resource_ids = [r.id for r in resources_list]
        domain = domain + [
            ('calendar_id', 'in', [False, self.id]),
            ('resource_id', 'in', resource_ids),
            ('date_from', '<=', datetime_to_string(end_dt)),
            ('date_to', '>=', datetime_to_string(start_dt)),
        ]

        # retrieve leave intervals in (start_dt, end_dt)
        result = []
        for leave in self.env['resource.calendar.leaves'].search(domain):
            dt0 = string_to_datetime(leave.date_from).astimezone(tz)
            dt1 = string_to_datetime(leave.date_to).astimezone(tz)
            result.append((dt0, dt1, leave))
        return Intervals(result)


    def _attendance_intervals_batch(self, start_dt, end_dt, resources=None, domain=None, tz=None):
        """
            Return the attendance intervals in the given datetime range.
            The returned intervals are expressed in specified tz or in the resource's timezone.
        """
        self.ensure_one()
        domain = domain +[
            ('check_in', '>=', datetime_to_string(start_dt)),
            ('check_in', '<', datetime_to_string(end_dt)),
        ]

        # retrieve leave intervals in (start_dt, end_dt)
        result = []
        for attd in self.env['hr.attendance'].search(domain):
            tz = tz if tz else timezone((self).tz)
            dt0 = string_to_datetime(attd.check_in).astimezone(tz)
            dt1 = string_to_datetime(attd.check_out).astimezone(tz)
            result.append((dt0, dt1, attd))
        return Intervals(result)


    def get_work_hours_count(self, start_dt, end_dt, compute_leaves=True, domain=None, employee = None):
        """
            `compute_leaves` controls whether or not this method is taking into
            account the global leaves.

            `domain` controls the way leaves are recognized.
            None means default value ('time_type', '=', 'leave')

            Counts the number of work hours between two datetimes.
        """
        self.ensure_one()
        # Set timezone in UTC if no timezone is explicitly given
        if not start_dt.tzinfo:
            start_dt = start_dt.replace(tzinfo=utc)
        if not end_dt.tzinfo:
            end_dt = end_dt.replace(tzinfo=utc)
        delta = timedelta(hours=24)
        working_hours = 0
        while start_dt <= end_dt:
            working_hours += employee and employee.contract_id.resource_calendar_id.hours_per_day or 8
            start_dt += delta
        return working_hours

ResourceCalendar

class ResourceMixins(models.AbstractModel):
    _inherit = "resource.mixin"

    def list_leaves(self, from_datetime, to_datetime, calendar=None, domain=None):
        """
            By default the resource calendar is used, but it can be
            changed using the `calendar` argument.

            `domain` is used in order to recognise the leaves to take,
            None means default value ('time_type', '=', 'leave')

            Returns a list of tuples (day, hours, resource.calendar.leaves)
            for each leave in the calendar.
        """
        resource = self.resource_id
        calendar = calendar or self.resource_calendar_id

        # naive datetimes are made explicit in UTC
        if not from_datetime.tzinfo:
            from_datetime = from_datetime.replace(tzinfo=utc)
        if not to_datetime.tzinfo:
            to_datetime = to_datetime.replace(tzinfo=utc)

        leaves = calendar._leave_intervals_batch(from_datetime, to_datetime, resource, domain)[resource.id]
        result = []
        for start, stop, leave in leaves:
            hours = (stop - start).total_seconds() / 3600
            result.append((start.date(), hours, leave))
        return result


ResourceMixins