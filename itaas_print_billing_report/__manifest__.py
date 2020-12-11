# -*- coding: utf-8 -*-

# Part of ITAAS (www.itaas.co.th)

{
    'name' : 'Print Accounting Billing Report',
    'version' : '11.0.1',
    'price' : 'Free',
    'currency': 'THB',
    'category': 'Accounting',
    'summary' : 'Print Accounting Billing Report',
    'description': """
                Accounting Report:
                    - Creating Accounting Billing Report
Tags: 
Stock report
            """,
    'author' : 'IT as a Service Co., Ltd.',
    'website' : 'www.itaas.co.th',
    'depends' : ['sale','purchase','base','account','account_accountant','thai_accounting'],
    'data' : [
        'report/report_reg.xml',
        'report/customer_billing_report.xml',
        'views/res_company.xml',


    ],


    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
