# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields, _
from odoo.exceptions import ValidationError


class CreateSaleQuotation(models.TransientModel):
    _name = "create.sale.quotation"

    def create_quotation(self):
        for line in self.line_ids:
            if line.order_qty <= 0:
                raise ValidationError(_('''New Quotation Quantity must be greater than zero for all the products'''))
            if not line.partner_id:
                raise ValidationError(_('''Please add Customer in all lines'''))
            if line.order_qty > line.remaining_qty:
                raise ValidationError(_('''You can not order '%s' quantity of '%s' because Remaining Quantity of it is '%s' ''') %
                                      (line.order_qty, line.product_id.name, line.remaining_qty))
        customer_dict = {}
        for line in self.line_ids:
            if line.partner_id.id not in customer_dict:
                customer_dict.update({line.partner_id.id: [line]})
            else:
                customer_dict[line.partner_id.id].append(line)
        if customer_dict:
            blanket_id = self.line_ids[0].sale_line_id.order_id
            consumed_qty_dict = {}
            new_quotations = []
            for value in customer_dict:
                partner_id = self.env['res.partner'].browse(int(value))
                if partner_id:
                    data = []
                    for line in customer_dict[value]:
                        data.append((0, 0,{'product_id': line.product_id.id,
                                           'product_uom': line.sale_line_id.product_uom.id,
                                           'product_uom_qty': line.order_qty,
                                           'price_unit': line.sale_line_id.price_unit,
                                           'name': line.sale_line_id.name,
                        }))
                        consumed_qty_dict.update({line.sale_line_id.id: line.order_qty})
                    if data:
                        quotation_id = self.env['sale.order'].create({'partner_id': partner_id.id,
                                                                      'order_line': data})
                        if quotation_id:
                            new_quotations.append(quotation_id.id)

            if new_quotations:
                for quote in new_quotations:
                    blanket_id.blanket_order_ids = [(4, quote)]
                if consumed_qty_dict:
                    for qty_val in consumed_qty_dict:
                        blanket_line_id = self.env['sale.order.line'].browse(int(qty_val))
                        if blanket_line_id:
                            blanket_line_id.consumed_qty += float(consumed_qty_dict[qty_val])

    line_ids = fields.One2many('create.sale.quotation.line', 'create_quote_id', string="Lines")


class CreateSaleQuotationLine(models.TransientModel):
    _name = "create.sale.quotation.line"

    create_quote_id = fields.Many2one('create.sale.quotation', string='Create Sale Quotation')
    sale_line_id = fields.Many2one('sale.order.line', string='Sale Order Line')
    product_id = fields.Many2one('product.product', related='sale_line_id.product_id')
    remaining_qty = fields.Float(string='Remaining Quantity', related='sale_line_id.remaining_qty')
    partner_id = fields.Many2one('res.partner', string='Customer')
    order_qty = fields.Float(string='New Quotation Quantity')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
