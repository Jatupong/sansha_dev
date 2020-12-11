# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from odoo import fields, api, models, _

class PrintSaleReprot(models.Model):
    _name = 'print.sale.report'

    report_type = fields.Selection([('quotation','ใบเสนอราคา / ใบสั่งขาย'),('temporary','ใบส่งของชั่วคราว')], String="Report type", default='quotation')
    show_product_code_on_sale = fields.Boolean(string='Show Code in Report')

    def print_report_pdf(self):
        data = {
            'show_product_code_on_sale': self.show_product_code_on_sale,
            'sale_orders': self._context.get('active_ids', []),
        }
        if self.report_type == 'temporary':
            return self.env.ref('itaas_print_sale_report.quotations_temporary_report').report_action(self, data=data, config=False)
        else:
            return self.env.ref('itaas_print_sale_report.quotations_report').report_action(self, data=data, config=False)


class PrintQuotationTemporary(models.AbstractModel):
    _name = 'report.itaas_print_sale_report.quotations_temporary_report_id'

    def _get_report_values(self, docids, data=None):
        if not docids:
            sale_orders = self.env['sale.order'].browse(data['sale_orders'])
            doc_ids = sale_orders.ids
            docs = sale_orders
            show_product_code_on_sale = data['show_product_code_on_sale']
            is_action = True
        else:
            doc_ids = docids
            docs = self.env['sale.order'].browse(docids)
            show_product_code_on_sale = False
            is_action = False

        return {
            'doc_ids': doc_ids,
            'doc_model': 'sale.order',
            'docs': docs,
            'show_product_code_on_sale': show_product_code_on_sale,
            'is_action': is_action,
        }


class PrintQuotationsReport(models.AbstractModel):
    _name = 'report.itaas_print_sale_report.quotations_report_id'

    def _get_report_values(self, docids, data=None):
        if not docids:
            sale_orders = self.env['sale.order'].browse(data['sale_orders'])
            doc_ids = sale_orders.ids
            docs = sale_orders
            show_product_code_on_sale = data['show_product_code_on_sale']
            is_action = True
        else:
            doc_ids = docids
            docs = self.env['sale.order'].browse(docids)
            show_product_code_on_sale = False
            is_action = False

        return {
            'doc_ids': doc_ids,
            'doc_model': 'sale.order',
            'docs': docs,
            'show_product_code_on_sale': show_product_code_on_sale,
            'is_action': is_action,
        }