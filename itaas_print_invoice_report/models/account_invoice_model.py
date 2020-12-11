from odoo import models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice.line'

    discount_amount = fields.Float(string='จำนวนเงินส่วนลด')



