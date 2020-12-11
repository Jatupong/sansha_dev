# -*- coding: utf-8 -*-
# Copyright (C) 2019-Today  itaas
{
    'name': 'Itaas Partner Detail Address',
    'version': '13.0.2.0',
    'sequence': 1,
    'category': 'base',
    'summary': 'Partner Detail Address',
    'author': 'ITAAS',
    'website': 'http://www.itaas.co.th/',
    'description': """
This module is for partner detail address
        """,
    'depends': ['contacts'],
    'data': [
        'views/res_company_view.xml',
        'views/res_district_view.xml',
        'views/res_subdistrict_view.xml',
        'views/res_partner_view.xml',
        'data/res_country_data.xml',
        'data/res_state_data.xml',
        'data/res_district_data.xml',
        'data/res_sub_district_data.xml',
        'security/ir.model.access.csv'
    ],
    'images': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
