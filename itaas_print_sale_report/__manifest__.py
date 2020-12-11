# -*- coding: utf-8 -*-

# Part of ITAAS (www.itaas.co.th)

{
    'name' : 'Itaas Print Sales Report',
    'version' : '13.0.1.1',
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
    'depends' : ['sale','base','itaas_company_setting'],
    'data' : [
        'views/res_company.xml',
        'views/res_partner.xml',
        'views/sale_order_view.xml',

        'wizard/print_sale_report_view.xml',

        'report/report_reg.xml',
        'report/quotation_report.xml',
        'report/quotation_temporary_report.xml',

        'security/ir.model.access.csv',
    ],


    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
