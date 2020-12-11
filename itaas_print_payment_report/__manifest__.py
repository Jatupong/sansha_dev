# -*- coding: utf-8 -*-

# Part of ITAAS (www.itaas.co.th)

{
    'name' : 'Print Invoice and Payment Report',
    'version' : '11.0.1',
    'price' : 'Free',
    'currency': 'THB',
    'category': 'Accounting',
    'summary' : 'Print Payment Report',
    'description': """
                Accounting Invoice and Payment:
                    - Creating Invoice and Payment Report
Tags: 

            """,
    'author' : 'IT as a Service Co., Ltd.',
    'website' : 'www.itaas.co.th',
    'depends' : ['base','account','account_accountant','thai_accounting'],
    'data' : [
        'report/report_reg.xml',
        'report/receipt_report.xml',
        'report/tax_invoice_receipt_report.xml',
        'views/res_company.xml',

    ],


    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
