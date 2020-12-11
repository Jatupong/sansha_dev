# -*- coding: utf-8 -*-
from openerp import fields, api, models, _
from bahttext import bahttext



class Account_cheque_statement(models.Model):
    _inherit ="account.cheque.statement"



    def baht_text(self, amount_total):
        return bahttext(amount_total)

    def get_uppercase(self, vals):
        if vals:
            val = vals.upper()
        else:
            val = vals
        print(val)
        return val

    def get_date_format(self, vals):
        txt = str(vals)
        for v in txt:
            txt_2 = str(txt[8]) + ' ' + str(txt[9]) + ' ' + str(txt[5])+ ' ' + str(txt[6]) + ' ' + str(txt[0])+ ' ' + str(txt[1]) + ' ' + str(txt[2]) + ' ' + str(txt[3])

        return txt_2

    def baht_text(self, amount_total):
        return bahttext(amount_total)

    # @api.model
    # def create(self, vals):
    #     if vals.get('partner_id', False):
    #         vals['name_for_cheque'] = self.env['res.partner'].browse(vals['partner_id']).name_for_cheque
    #     return super(Account_cheque_statement, self).create(vals)
