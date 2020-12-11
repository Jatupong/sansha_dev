# -*- coding: utf-8 -*-

{
    'name': 'Blanket Sale Order',
    'version': '13.0.1.0',
    'sequence': 1,
    'category': 'Sales',
    'description':
        """
        This Module add below functionality into odoo

        1.Blanket Sale Order\n

odoo sale Blanket order
odoo Blanket order
odoo blanket sale order
blanket sale order 
sale blanket order
order blanket in odoo 
order process in blanket 

    """,
    'summary': 'Odoo app allow Blanket Sale Order aggreement between Seller and Customer, sale Blanket order, Blanket order, long term Sale order, Blanket Order',
    'depends': ['sale_management'],
    'data': [
        'data/blanket_sequence_view.xml',
        'views/blanket_order_view.xml',
        'views/sale_view.xml',
        'wizard/create_sale_quotation_view.xml',
        'data/cron_blanket_expiry_view.xml',
        ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
