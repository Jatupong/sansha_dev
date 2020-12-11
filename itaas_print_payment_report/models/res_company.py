# -*- coding: utf-8 -*-
from openerp import fields, api, models, _
from bahttext import bahttext
from openerp.exceptions import UserError
from datetime import datetime, date

class res_company(models.Model):
    _inherit ="res.company"

    receipt_no_form = fields.Char(string='Receipt No. Form')
    tax_inv_receipt_no_form = fields.Char(string='Tax Invoice & Receipt No. Form')
    show_currency_on_payment = fields.Boolean(string='Show Currency in Payment')
    show_date_auto_payment = fields.Boolean(string='Show Date Payment')




