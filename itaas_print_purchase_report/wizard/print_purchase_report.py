# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from odoo import fields, api, models, _

class PrintSaleReprot(models.Model):
    _name = 'print.purchase.report'

    report_type = fields.Selection([('purchase','ใบสั่งซื้อ'),
                                    ('temporary','ใบส่งของชั่วคราว'),
                                    ('dummy','ใบส่งของชั่วคราว ระบุผู้ขาย')], String="Report type", default='purchase')
    show_product_code_on_purchase = fields.Boolean(string='Show Code in Report')
    partner_id = fields.Many2one('res.partner', string='Partner')

    @api.model
    def default_get(self, fields_list):
        res = super(PrintSaleReprot, self).default_get(fields_list)
        partner = self.env['res.partner'].search([('is_purchase_report','=',True)], limit=1)
        res.update({'partner_id': partner.id, })
        return res

    def print_report_pdf(self):
        data = {
            'partner_id': self.partner_id.id or False,
            'show_product_code_on_purchase': self.show_product_code_on_purchase,
            'purchase_orders': self._context.get('active_ids', []),
        }
        if self.report_type == 'purchase':
            return self.env.ref('itaas_print_purchase_report.purchase_order_report').report_action(self, data=data, config=False)
        elif self.report_type == 'temporary':
            return self.env.ref('itaas_print_purchase_report.purchase_temporary_report').report_action(self, data=data, config=False)
        else:
            return self.env.ref('itaas_print_purchase_report.purchase_dummy_report').report_action(self, data=data, config=False)


class PrintPurchaseReport(models.AbstractModel):
    _name = 'report.itaas_print_purchase_report.purchase_order_report_id'

    def _get_report_values(self, docids, data=None):
        if not docids:
            sale_orders = self.env['purchase.order'].browse(data['purchase_orders'])
            doc_ids = sale_orders.ids
            docs = sale_orders
            show_product_code_on_purchase = data['show_product_code_on_purchase']
            is_action = True
        else:
            doc_ids = docids
            docs = self.env['purchase.order'].browse(docids)
            show_product_code_on_purchase = False
            is_action = False

        return {
            'doc_ids': doc_ids,
            'doc_model': 'purchase.order',
            'docs': docs,
            'show_product_code_on_purchase': show_product_code_on_purchase,
            'is_action': is_action,
        }


class PrintPurchaseTemporaryReport(models.AbstractModel):
    _name = 'report.itaas_print_purchase_report.purchase_temporary_report_id'

    def _get_report_values(self, docids, data=None):
        if not docids:
            sale_orders = self.env['purchase.order'].browse(data['purchase_orders'])
            doc_ids = sale_orders.ids
            docs = sale_orders
            show_product_code_on_purchase = data['show_product_code_on_purchase']
            is_action = True
        else:
            doc_ids = docids
            docs = self.env['purchase.order'].browse(docids)
            show_product_code_on_purchase = False
            is_action = False

        return {
            'doc_ids': doc_ids,
            'doc_model': 'purchase.order',
            'docs': docs,
            'show_product_code_on_purchase': show_product_code_on_purchase,
            'is_action': is_action,
        }

class PrintPurchaseDummyReport(models.AbstractModel):
    _name = 'report.itaas_print_purchase_report.purchase_dummy_report_id'

    def _get_report_values(self, docids, data=None):
        if not docids:
            sale_orders = self.env['purchase.order'].browse(data['purchase_orders'])
            doc_ids = sale_orders.ids
            docs = sale_orders
            show_product_code_on_purchase = data['show_product_code_on_purchase']
            is_action = True
            partner_id = self.env['res.partner'].browse(data['partner_id'])
        else:
            doc_ids = docids
            docs = self.env['purchase.order'].browse(docids)
            show_product_code_on_purchase = False
            is_action = False
            partner_id = False

        print('partner_id : ',partner_id)
        return {
            'doc_ids': doc_ids,
            'doc_model': 'purchase.order',
            'docs': docs,
            'show_product_code_on_purchase': show_product_code_on_purchase,
            'is_action': is_action,
            'partner_id': partner_id,
        }