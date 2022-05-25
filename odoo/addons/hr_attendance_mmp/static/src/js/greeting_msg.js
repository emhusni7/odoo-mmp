/** @odoo-module **/
import time from 'web.time';
import core from 'web.core';
import field_utils from 'web.field_utils';
import GreetingMessage from 'hr_attendance.greeting_message';

var Greeting = GreetingMessage.extend({
    events: {
        "click .o_hr_attendance_button_dismiss": function() {
        this.do_action('hr_attendance_mmp.hr_attendance_action_kiosk_mode_mmp', {clear_breadcrumbs: true}); },
    },
    init: function(parent, action) {
            var self = this;
            this._super.apply(this, arguments);
            this.activeBarcode = true;

            // if no correct action given (due to an erroneous back or refresh from the browser), we set the dismiss button to return
            // to the (likely) appropriate menu, according to the user access rights
            if(!action.attendance) {
                this.next_action = 'hr_attendance_mmp.hr_attendance_action_kiosk_mode_mmp'
                this.activeBarcode = false;
                return;
            }
            this.next_action = 'hr_attendance_mmp.hr_attendance_action_kiosk_mode_mmp';
            // no listening to barcode scans if we aren't coming from the kiosk mode (and thus not going back to it with next_action)
            if (this.next_action != 'hr_attendance_mmp.hr_attendance_action_kiosk_mode_mmp' && this.next_action.tag != 'hr_attendance_kiosk_mode_mmp') {
                this.activeBarcode = false;
            }

        }
})
core.action_registry.add('hr_attendance_greeting_message', Greeting);
export default Greeting;
