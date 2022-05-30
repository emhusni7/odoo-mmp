/** @odoo-module */

import CalendarController from 'web.CalendarController';
import viewRegistry from 'web.view_registry';
import CalendarView from "web.CalendarView";
import core from "web.core";
import dialogs from 'web.view_dialogs';
var _t = core._t;
var QWeb = core.qweb;
//var CalendarController = require("web.CalendarController");


var CalendarFormController = CalendarController.extend({
    events: _.extend({}, CalendarController.prototype.events, {
            'click .btn-time-off': '_onNewTimeOff',
//            'click .btn-allocation': '_onNewAllocation',
        }),

        /**
         * @override
         */
        start: function () {
            this.$el.addClass('o_timeoff_calendar');
            return this._super(...arguments);
        },

        //--------------------------------------------------------------------------
        // Public
        //--------------------------------------------------------------------------

         /**
         * Render the buttons and add new button about
         * time off and allocations request
         *
         * @override
         */

        renderButtons: function ($node) {
            this._super.apply(this, arguments);

            $(QWeb.render('hr_holidays.dashboard.calendar.button', {
                time_off: _t('New Time Off'),
//                request: _t('Allocation Request'),
            })).appendTo(this.$buttons);

            if ($node) {
                this.$buttons.appendTo($node);
            } else {
                this.$('.o_calendar_buttons').replaceWith(this.$buttons);
            }
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        _getNewTimeOffContext: function() {
            let date_from = moment().set({
                'hour': 0,
                'minute': 0,
                'second': 0
            });
            date_from.subtract(this.getSession().getTZOffset(date_from), 'minutes');
            date_from = date_from.locale('en').format('YYYY-MM-DD HH:mm:ss');
            let date_to = moment().set({
                'hour': 23,
                'minute': 59,
                'second': 59
            });
            date_to.subtract(this.getSession().getTZOffset(date_to), 'minutes');
            date_to = date_to.locale('en').format('YYYY-MM-DD HH:mm:ss');
            return {
                'default_date_from': date_from,
                'default_date_to': date_to,
                'lang': this.context.lang
            }
        },

        /**
         * Action: create a new time off request
         *
         * @private
         */
        _onNewTimeOff: function () {
            this._rpc({
                model: 'ir.ui.view',
                method: 'get_view_id',
                args: ['hr_holidays.hr_leave_view_form_manager'],
            }).then((ids) => {
                this.timeOffDialog = new dialogs.FormViewDialog(this, {
                    res_model: "hr.leave",
                    view_id: ids,
                    context: this._getNewTimeOffContext(),
                    title: _t("New time off"),
                    disable_multiple_selection: true,
                    on_saved: () => {
                        this.reload();
                    },
                });
                this.timeOffDialog.open();
            });
        },

        /**
         * Action: create a new allocation request
         *
         * @private
         */
        _onNewAllocation: function () {
            let self = this;

            self._rpc({
                model: 'ir.ui.view',
                method: 'get_view_id',
                args: ['hr_holidays.hr_leave_allocation_view_form_dashboard'],
            }).then(function(ids) {
                self.allocationDialog = new dialogs.FormViewDialog(self, {
                    res_model: "hr.leave.allocation",
                    view_id: ids,
                    context: {
                        'default_state': 'confirm',
                        'lang': self.context.lang,
                    },
                    title: _t("New Allocation"),
                    disable_multiple_selection: true,
                    on_saved: function() {
                        self.reload();
                    },
                });
                self.allocationDialog.open();
            });
        },

        /**
         * @override
         */
        _setEventTitle: function () {
            return _t('Time Off Request');
        },
});


var TimeOffCalendarAllView = CalendarView.extend({
        config: _.extend({}, CalendarView.prototype.config, {
            Controller: CalendarFormController,
        }),
    });

viewRegistry.add('time_off_calendar', TimeOffCalendarAllView);
export default TimeOffCalendarAllView;