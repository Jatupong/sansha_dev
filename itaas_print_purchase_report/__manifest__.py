# -*- coding: utf-8 -*-

# Part of ITAAS (www.itaas.co.th)

{
    'name' : 'Print Purchase Report',
    'version' : '13.0.1.1',
    'price' : 'Free',
    'currency': 'THB',
    'category': 'Purchase Report',
    'summary' : 'Print Purchase Report',
    'description': """
                PR and Purchase Order Report:
Tags: 
Stock report
            """,
    'author' : 'IT as a Service Co., Ltd.',
    'website' : 'www.itaas.co.th',
    'depends' : ['purchase','base','itaas_company_setting','purchase_discount'],
    'data' : [
        'views/res_company.xml',
        'views/res_partner_view.xml',
        'views/purchase_order_view.xml',

        'wizard/print_purchase_report_view.xml',

        'report/report_reg.xml',
        'report/purchase_order_report.xml',
        'report/purchase_dummy_report.xml',
        'report/purchase_temporary_report.xml',

        'security/ir.model.access.csv',
    ],


    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
