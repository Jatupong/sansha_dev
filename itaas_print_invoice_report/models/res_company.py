# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from bahttext import bahttext
from odoo.exceptions import UserError
from datetime import datetime, date

class res_company(models.Model):
    _inherit ="res.company"

    invoice_no_form = fields.Char(string='Invoice No. Form')
    invoice_and_tax_invoice_no_form = fields.Char(string='Invoice and Tax No. Form')
    tax_invoice_no_form = fields.Char(string='Tax Invoice No. Form')
    tax_invoice_and_receipt_no_form = fields.Char(string='Tax Invoice & Receipt No. Form')
    show_currency_on_invoice = fields.Boolean(string='Show Currency in Invoice')
    show_date_auto_invoice = fields.Boolean(string='Show Date Invoice')
    credit_no_form = fields.Char(string='Credit No. Form')
    debit_no_form = fields.Char(string='Debit No. Form')



