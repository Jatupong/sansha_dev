# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class ChequeAdvanceConfirmOrder(models.TransientModel):
    _name = "cheque.advance.confirm.order"
    _description = "Cheque Advance Confirm Order"

    # @api.model
    # def _count(self):
    #     return len(self._context.get('active_ids', []))

    # @api.model
    # def _get_advance_payment_method(self):
    #     if self._count() == 1:
    #         sale_obj = self.env['sale.order']
    #         order = sale_obj.browse(self._context.get('active_ids'))[0]
    #         if all([line.product_id.invoice_policy == 'order' for line in order.order_line]) or order.invoice_count:
    #             return 'all'
    #     return 'delivered'
    #
    # @api.model
    # def _default_product_id(self):
    #     product_id = self.env['ir.config_parameter'].sudo().get_param('sale.default_deposit_product_id')
    #     return self.env['product.product'].browse(int(product_id))
    #
    # @api.model
    # def _default_deposit_account_id(self):
    #     return self._default_product_id().property_account_income_id
    #
    # @api.model
    # def _default_deposit_taxes_id(self):
    #     return self._default_product_id().taxes_id


    # order_date = fields.Date(string='Order Date')
    def post_cheque_to_bank(self):
        cheque_ids = self.env['account.cheque.statement'].browse(self._context.get('active_ids', []))

        for order in cheque_ids.filtered(lambda x: x.state == 'open'):
            order.action_post()
        return {'type': 'ir.actions.act_window_close'}


    def confirm_order(self):
        cheque_ids = self.env['account.cheque.statement'].browse(self._context.get('active_ids', []))

        for order in cheque_ids.filtered(lambda x: x.state in ('open','post')):
            order.action_validate()
        return {'type': 'ir.actions.act_window_close'}

