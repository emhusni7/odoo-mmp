# -*- coding: utf-8 -*-

{
    'name': 'Recruitement For MMP ',
    'category': 'Generic Modules/Human Resources',
    'version': '15.0.1.0.0',
    'author': 'Odoo SA,Recruitment Custom MMP',
    'company': 'Mega Marine Pride',
    'maintainer': 'Mega Marine Pride',
    'summary': 'Manage your employsee payroll records',
    'description': "Odoo Req",
    'depends': [
        'hr',
        'hr_recruitment',
        'hr_contract_mmp',
        'hr_payroll_community'
    ],
    'assets': {
        'web.assets_backend':['hr_recruitment_mmp/static/src/css/style.css']
    },
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'report/report.xml',
        'wizard/wiz_ptk_mmp.xml',
        'views/hr_divisi_views.xml',
        'views/hr_recruitment_views.xml',
        'views/employee.xml',
        'views/job.xml',
        'views/ptk.xml',
    ],

    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
