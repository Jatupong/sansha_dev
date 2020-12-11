# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today  ITAAS (<http://www.itaas.co.th/>).
{
    "name": "Thailand Accounting Enhancement for Odoo Enterprise",
    "category": 'Accounting',
    'summary': 'Thailand Accounting Enhancement.',
    "description": """
        .
    """,
    "sequence": 1,
    "author": "IT as a Service Co., Ltd.",
    "website": "http://www.itaas.co.th/",
    "version": '13.0.1.0',
    "depends": ['account','account_payment','account_asset','account_accountant'],
    "external_dependencies" : {
        'python' : ['bahttext',
                    'num2words',
                    'xlrd'],
    },
    "data": [
        'sequence.xml',
        'views/res_company_view.xml',
        'views/res_partner_view.xml',
        #########################Next View###################
        'views/account_account_view.xml',
        'views/account_journal_view.xml',
        'views/account_tax_view.xml',
        'views/account_move_view.xml',
        'views/account_payment_view.xml',
        'views/customer_billing_view.xml',
        'views/account_cheque_statement_view.xml',
        # 'views/account_asset_asset_view.xml',
        # 'wizard/check_multiple_confirm_views.xml',
        ######################print_accounting_asset###############
        # 'report/asset_labels_report.xml',
        # 'report/asset_report.xml',
        # 'wizard/asset_report_view.xml',
        ############################################################
        # data fro preload ###
        'data/account_wht_data.xml',
        # security access and rule
        'security/ir.model.access.csv',


    ],
    'qweb': [],
    "installable": True,
    "application": True,
    "auto_install": False,
}
