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
    'depends':[
        'hr_payroll_community',
        'hr_contract_mmp',
        'hr_recruitment_mmp',
        'hr_attendance_mmp',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/wizard_change_schedule.xml',
        'views/salary_rule_mmp.xml',
        'views/salary_structure.xml',
        'views/payslip.xml',
        'views/work_type.xml',
        'views/contract_schedule.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
