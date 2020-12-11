# -*- coding: utf-8 -*-

# Part of ITAAS (www.itaas.co.th)

{
    'name' : 'Print Report General Account',
    'version' : '1.0',
    'price' : 'Free',
    'currency': 'THB',
    'category': 'Quotations',
    'summary' : 'Print Report Account',
    'description': """
                Print Report General Account:
                    - Print Report General Account
Tags: 
Stock report
            """,
    'author' : 'IT as a Service Co., Ltd.',
    'website' : 'www.itaas.co.th',
    'depends' : ['sale','base','account','purchase','odoo_report_xlsx','account_accountant','thai_accounting'],
    'data' : ['report/report_reg.xml',
              'report/debitcredit_report01_inherit.xml',
              'report/debitcredit_report02_inherit.xml',
              'report/debitcredit_report03_inherit.xml',
              'report/debitcredit_report04_inherit.xml',
              'report/debitcredit_report05_inherit.xml',

              'report/debitcredit_receipt_voucher.xml',
              'report/debitcredit_general_voucher.xml',

              'report/debitcredit_account_receivable_voucher.xml',
              'report/debitcredit_payment_report.xml',
              'report/debitcredit_payment_voucher.xml',


              # 'views/view_account_vat.xml',
              'views/account_move_view.xml',

              'sequence.xml',
              ],


    #'report/productvariant_report.xml'],
    'installable' : True,
    'application' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
