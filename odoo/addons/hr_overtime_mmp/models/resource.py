from odoo import models, api, fields
from odoo.addons.resource.models.resource import Intervals, datetime_to_string, string_to_datetime
from pytz import  timezone
import pytz



class IntervalMMP(Intervals):
    def _check_onAttDays(self, overtime):
        for idx, x in enumerate(self._items):
            for y in overtime._items:
                if x[0].date() == y[0].date() and x[1].date() == y[1].date():
                    del self._items[idx]
        return Intervals(self._items)


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    def _overtime_intervals_batch(self, start_dt, end_dt, resources=None, domain=None, tz=None):
        """
            Return the attendance intervals in the given datetime range.
            The returned intervals are expressed in specified tz or in the resource's timezone.
        """
        localtz = pytz.timezone('Asia/Jakarta')
        self.ensure_one()
        domain = domain + [
            ('date_from', '>=', datetime_to_string(start_dt)),
            ('date_to', '<=', datetime_to_string(end_dt)),
            ('overtime_bulk_id.state','=','approved')
        ]

        localtz = pytz.timezone('Asia/Jakarta')
        # retrieve leave intervals in (start_dt, end_dt)
        result = []
        for attd in self.env['hr.overtime'].search(domain):

            tz = tz if tz else timezone((self).tz)
            dt0 = string_to_datetime(attd.date_from).astimezone(tz)
            dt1 = string_to_datetime(attd.date_to).astimezone(tz)
            #convert to localdate
            result.append((dt0.astimezone(localtz), dt1.astimezone(localtz), attd))
        return Intervals(result)

ResourceCalendar
