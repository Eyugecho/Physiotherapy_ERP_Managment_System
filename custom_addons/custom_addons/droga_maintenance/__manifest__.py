# -*- coding: utf-8 -*-
{
    'name': "Property Managment",

    'summary': """
        This Model is used for managing Property""",

    'description': """
        Property Managment
    """,

    'author': "Nathan",
    'website': "https://drogapharma.com/",
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['maintenance'],

  
    'data': [
        
        'views/views.xml',
        'views/preport_menu.xml',
        'security/ir.model.access.csv',
    ],
   
}
