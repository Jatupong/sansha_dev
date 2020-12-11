# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)
{
    "name": "Itaas Print Bank",
    "author": "Itaas Print Bank",
    "version": "13.0.0.1",
    "category": "mrp",
    "website": "www.itaas.co.th",
    "depends": ['account','hr'],
    "data": [
        'report/debitcredit_report06.xml',
        'report/report_reg.xml',
        'views/sequence.xml',
        'views/cash_register.xml',

    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
