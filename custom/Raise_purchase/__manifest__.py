# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Rise Sales',
    'version': '1.0',
    'category': 'Services',
    'summary': 'Raise',
    'description': 'Bridge created to convert tickets to tasks and tasks to tickets',
    'depends': ['purchase','sale_management'],
    'data': [

        'securityy/ir.model.access.csv',
        "raise.xml",
        "report.xml",
        "commercial.xml",

    ],
    'installable': True,
    'license': '',
}
