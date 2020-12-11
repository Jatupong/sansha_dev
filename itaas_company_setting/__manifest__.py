# -*- coding: utf-8 -*-

# Part of ITAAS (www.itaas.co.th)

{
    'name' : 'General Company Setting',
    'version' : '13.0.1.0',
    'price' : 'Free',
    'currency': 'THB',
    'category': 'General Company Setting',
    'summary' : 'General Company Setting',
    'description': """
                General Company Setting:
Tags: 
Stock report
            """,
    'author' : 'IT as a Service Co., Ltd.',
    'website' : 'www.itaas.co.th',
    'depends' : ['base'],
    'data' : [
        'views/res_company_view.xml',
    ],


    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
