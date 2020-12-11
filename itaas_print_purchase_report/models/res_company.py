# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from bahttext import bahttext
from odoo.exceptions import UserError
from datetime import datetime, date

class res_company(models.Model):
    _inherit ="res.company"

    purchase_order_no_form = fields.Char(string='Purchase Order No. Form')
    show_product_code_on_purchase = fields.Boolean(string='Show Code in Purchase')
    show_currency_on_purchase = fields.Boolean(string='Show Currency in Purchase')
    show_date_auto_purchase = fields.Boolean(string='Show Date Purchase')



