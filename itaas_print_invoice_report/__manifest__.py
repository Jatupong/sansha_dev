# -*- coding: utf-8 -*-

# Part of ITAAS (www.itaas.co.th)

{
    'name' : 'Print Accounting - Invoice Report',
    'version' : '11.0.1',
    'price' : 'Free',
    'currency': 'THB',
    'category': 'Accounting',
    'summary' : 'Print Accounting Invoice Report',
    'description': """
                Accounting Report:
                    - Creating Accounting Invoice Report
Tags: 
Stock report
            """,
    'author' : 'IT as a Service Co., Ltd.',
    'website' : 'www.itaas.co.th',
    'depends' : ['sale','purchase','base','account','account_accountant'],
    'data' : [
        'views/res_company.xml',
        # 'views/show_discount_amount.xml',
        'report/report_reg.xml',
        'report/invoice_and_tax_invoice_report.xml',
        'report/invoice_report.xml',
        'report/tax_invoice_report.xml',
        'report/tax_invoice_and_receipt_report.xml',
        'report/creditnote_report.xml',
        'report/debitnote_report.xml',
        'report/receipt_report.xml',

        #################This is example for DOT ######
        # 'report/invoice_receipt_dot.xml',
    ],


    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
