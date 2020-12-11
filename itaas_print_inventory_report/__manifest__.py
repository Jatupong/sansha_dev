# -*- coding: utf-8 -*-

# Part of ITAAS (www.itaas.co.th)

{
    'name' : 'Print Stock Picking Report',
    'version' : '13.0.1.0',
    'price' : 'Free',
    'currency': 'THB',
    'category': 'Accounting',
    'summary' : 'Print Stock Picking Report',
    'description': """
                Accounting Report:
                    - Creating Accounting Invoice Report
Tags: 
Stock report
            """,
    'author' : 'IT as a Service Co., Ltd.',
    'website' : 'www.itaas.co.th',
    'depends' : ['sale','purchase','base','account','account_accountant','thai_accounting'],
    'data' : [

        # 'report/product_bill_report.xml',
        # 'report/product_bill_report02.xml',
        'report/product_bill_report03.xml',
        'report/product_bill_report04.xml',
        # 'report/product_bill_report05.xml',
        'report/product_bill_report06.xml',
        # 'report/product_bill_report07.xml',
        'report/product_bill_report08.xml',
        'report/product_bill_report09.xml',
        'report/product_bill_report10.xml',
        # 'views/res_company.xml',

    ],


    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
