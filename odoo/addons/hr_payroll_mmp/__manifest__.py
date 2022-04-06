# -*- coding: utf-8 -*-

{
    'name': 'Odoo15 Payroll Custom For MMP ',
    'category': 'Generic Modules/Human Resources',
    'version': '15.0.1.0.0',
    'author': 'Odoo SA,Payroll Custom MMP',
    'company': 'Mega Marine Pride',
    'maintainer': 'Mega Marine Pride',
    'summary': 'Manage your employsee payroll records',
    'description': "Odoo 15 Payroll, Payroll, Odoo 15,Odoo Payroll, Odoo Community Payroll",
    'depends': [
        'hr_payroll_community',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/salary_rule_mmp.xml'
    ],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
