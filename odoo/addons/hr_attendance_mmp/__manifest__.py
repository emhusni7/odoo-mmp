# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Attendances FOR MMP',
    'version': '2.0',
    'category': 'Human Resources/Attendances MMP',
    'sequence': 240,
    'summary': 'Track employee attendance',
    'description': """
This module aims to manage employee's attendances.
==================================================

Keeps account of the attendances of the employees on the basis of the
actions(Check in/Check out) performed by them.
       """,
    'website': 'https://www.odoo.com/app/employees',
    'depends': ['hr'],
    'data': [
        'security/hr_attendance_security.xml',
        'security/ir.model.access.csv',
        'wizard/wizard_import_absen.xml',
        'views/hr_attendance.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
