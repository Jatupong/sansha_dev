# -*- coding: utf-8 -*-

# Part of ITAAS (www.itaas.co.th)

{
    'name' : 'Print Accounting Cheque Report',
    'version' : '13.0.1',
    'price' : 'Free',
    'currency': 'THB',
    'category': 'Accounting',
    'summary' : 'Print Accounting Report',
    'description': """
                Accounting Report:
                    - Creating Accounting Report
Tags: 
Stock report
            """,
    'author' : 'IT as a Service Co., Ltd.',
    'website' : 'www.itaas.co.th',
    'depends' : ['account','account_accountant','thai_accounting'],
    'data' : [
        'views/view_res_bank_form.xml',
        'report/report_reg.xml',
        'report/cheque_print.xml',
    ],


    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
