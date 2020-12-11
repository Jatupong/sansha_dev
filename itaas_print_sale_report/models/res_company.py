# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from bahttext import bahttext
from odoo.exceptions import UserError
from datetime import datetime, date

class res_company(models.Model):
    _inherit ="res.company"

    quotation_no_form = fields.Char(string='Quotation No. Form')
    sale_order_no_form = fields.Char(string='Sales Order No. Form')
    show_product_code_on_sale = fields.Boolean(string='Show Code in Quote')
    show_currency_on_sale = fields.Boolean(string='Show Currency in Quote')
    show_date_auto_sale = fields.Boolean(string='Show Date Quote')
    standard_tax = fields.Integer(string='Standard Tax %',default=7)


