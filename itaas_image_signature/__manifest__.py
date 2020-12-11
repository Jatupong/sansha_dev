# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

{
    'name' : 'User image signature',
    'version': '13.0.1.0',
    "category": "Sale",
    'author': 'IT as a Service Co., Ltd.',
    'website': 'http://www.itaas.co.th/',
    'license': 'AGPL-3',
    "depends": ['base',],
    "data": [
        # views res.users
        'views/res_users_view.xml',

    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
