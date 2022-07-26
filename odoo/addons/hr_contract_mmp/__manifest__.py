# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Employee Contracts Custom For MMP',
    'version': '1.0',
    'category': 'Human Resources/Contracts',
    'sequence': 337,
    'description': """   """,
    'website': 'https://www.odoo.com/app/employees',
    'depends': ['hr_contract'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/bpjs.xml',
        'views/contract.xml',
        'views/ptkp.xml',
        'views/employee.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
