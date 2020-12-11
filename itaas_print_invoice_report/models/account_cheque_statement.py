# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from bahttext import bahttext



class Account_cheque_statement(models.Model):
    _inherit ="account.cheque.statement"

    def baht_text(self, amount_total):
        return bahttext(amount_total)

    name_for_cheque = fields.Char(string='Name for Cheque')

    @api.model
    def create(self, vals):
        if vals.get('partner_id', False):
            vals['name_for_cheque'] = self.env['res.partner'].browse(vals['partner_id']).name_for_cheque
        return super(Account_cheque_statement, self).create(vals)

    def get_uppercase(self, vals):
        if vals:
            val = vals.upper()
        else:
            val = vals
        print(val)
        return val

