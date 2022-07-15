# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request


class HrAttendance(http.Controller):
    @http.route('/webhook', auth='none', type='json', methods=['POST'], csrf=False)
    def get_webhook(self):
        if request.method == 'POST':
            print("received data: ", request.json)
            return 'success', 200
