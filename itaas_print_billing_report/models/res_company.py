# -*- coding: utf-8 -*-
from openerp import fields, api, models, _
from bahttext import bahttext
from openerp.exceptions import UserError
from datetime import datetime, date

class res_company(models.Model):
    _inherit ="res.company"

    billing_no_form = fields.Char(string='Billing No. Form')
    show_currency_on_billing = fields.Boolean(string='Show Currency in Billing')
    show_date_auto_billing = fields.Boolean(string='Show Date Billing')
    payment_info = fields.Text(string='Payment Info')




