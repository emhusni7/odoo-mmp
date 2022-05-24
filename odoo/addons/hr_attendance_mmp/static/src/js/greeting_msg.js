odoo.define('hr_attendance_mmp.greeting_msg', function (require) {
"use strict";
var Greeting = require("hr_attendance.greeting_message")
var time = require('web.time');
var field_utils = require('web.field_utils');
var GreetingOv = Greeting.include({
    init: function(parent, action) {
        var self = this;
        this._super.apply(this, arguments);
        this.activeBarcode = true;

        // if no correct action given (due to an erroneous back or refresh from the browser), we set the dismiss button to return
        // to the (likely) appropriate menu, according to the user access rights
        if(!action.attendance) {
            this.activeBarcode = false;
            return;
        }

        this.next_action = action.next_action || 'hr_attendance_mmp.hr_attendance_action_kiosk_mode_mmp';
        // no listening to barcode scans if we aren't coming from the kiosk mode (and thus not going back to it with next_action)
        if (this.next_action != 'hr_attendance_mmp.hr_attendance_action_kiosk_mode_mmp' && this.next_action.tag != 'hr_attendance_kiosk_mode_mmp') {
            this.activeBarcode = false;
        }

        this.attendance = action.attendance;
        // We receive the check in/out times in UTC
        // This widget only deals with display, which should be in browser's TimeZone
        this.attendance.check_in = this.attendance.check_in && moment.utc(this.attendance.check_in).local();
        this.attendance.check_out = this.attendance.check_out && moment.utc(this.attendance.check_out).local();
        this.previous_attendance_change_date = action.previous_attendance_change_date && moment.utc(action.previous_attendance_change_date).local();

        // check in/out times displayed in the greeting message template.
        this.format_time = time.getLangTimeFormat();
        this.attendance.check_in_time = this.attendance.check_in && this.attendance.check_in.format(this.format_time);
        this.attendance.check_out_time = this.attendance.check_out && this.attendance.check_out.format(this.format_time);

        // extra hours amount displayed in the greeting message template.
        this.total_overtime_float = action.total_overtime; // Used for comparison in template
        this.total_overtime = field_utils.format.float_time(this.total_overtime_float)

        if (action.hours_today) {
            var duration = moment.duration(action.hours_today, "hours");
            this.hours_today = duration.hours() + ' hours, ' + duration.minutes() + ' minutes';
        }

        this.employee_name = action.employee_name;
        this.attendanceBarcode = action.barcode;
    },

});
return GreetingOv;
})