# -*- coding: utf-8 -*-

{
    'name': 'Recruitement For MMP ',
    'category': 'Generic Modules/Human Resources',
    'version': '15.0.1.0.0',
    'author': 'Odoo SA,Payroll Custom MMP',
    'company': 'Mega Marine Pride',
    'maintainer': 'Mega Marine Pride',
    'summary': 'Manage your employsee payroll records',
    'description': "Odoo Req",
    'depends': [
        'hr',
        'hr_recruitment'
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/hr_divisi_views.xml',
        'views/hr_recruitment_views.xml',
        'views/job.xml',
        'views/ptk.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
