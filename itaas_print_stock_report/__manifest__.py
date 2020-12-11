# -*- coding: utf-8 -*-

# Part of ITAAS (www.itaas.co.th)

{
    'name' : 'Print Stock Report',
    'version' : '11.0.1',
    'price' : 'Free',
    'currency': 'THB',
    'category': 'Sales Report',
    'summary' : 'Print Sales Report',
    'description': """
                Quotations and Sales Order Report:
Tags: 
Stock report
            """,
    'author' : 'IT as a Service Co., Ltd.',
    'website' : 'www.itaas.co.th',
    'depends' : ['stock','stock_landed_costs'],
    'data' : [
        # 'views/res_company.xml',
        # 'views/res_partner.xml',
        'report/report_reg.xml',
        'report/landed_costs_report.xml',
        'views/landed_costs_view.xml',
    ],


    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
