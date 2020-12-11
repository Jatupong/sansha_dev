# -*- coding: utf-8 -*-

# Part of ITAAS (www.itaas.co.th)

{
    'name' : 'Print Accounting Tax and WHT Report',
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
    'depends' : ['base','account','account_accountant','thai_accounting'],
    'data' : [
        'report/report_reg.xml',
        'report/sale_tax_report.xml',
        'report/purchase_tax_report.xml',
        'report/report_taxsummary.xml',
        'report/report_pnd3.xml',
        'report/report_pnd53.xml',
        'report/holdingtax3_report.xml',
        'report/holdingtax53_report.xml',
        # 'report/teejai_report.xml',
        # 'report/teejai_report02.xml',
        'report/teejai_report02_journal.xml',
        'report/teejai_report_journal.xml',
        # 'report/teejai_report03_journal.xml',
        'views/tax_report_view.xml',


    ],


    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
