# Copyright 2020 ITAAS info@itaas.co.th


{
    "name": "Display All Sequence on Journal",
    "version": "13.0.1.0.0",
    "category": "Account Management",
    "author": "ITAAS",
    "website": "https://itaas.co.th",
    "license": "AGPL-3",
    "depends": [
        'account',
    ],

    "data": [
        'security/ir.model.access.csv',
        'views/account_journal_view.xml',
    ],
    'installable': True,
}
