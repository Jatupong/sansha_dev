# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class report_sale_tax_report(models.AbstractModel):
    _name = 'report.itaas_print_tax_report.sale_tax_report_id'

    def get_amount_multi_currency(self,move_id):
        total_amount = 0.0
        tax_amount = 0.0
        for line in move_id.line_ids:
            total_amount += abs(line.debit)
            if line.account_id.sale_tax_report:
                tax_amount += abs(line.balance)
        return total_amount, tax_amount


    @api.model
    def _get_report_values(self, docids, data=None):
        print ('------_get_report_values ----> sales---')
        company_id = self.env.user.company_id
        operating_unit_id = False
        docs = False


        # step = self.env.user.company_id.invoice_step
        domain = [('account_id.sale_tax_report','=',True),('date','>=',data['date_from']),('date','<=',data['date_to']),('move_id.state','=','posted')]

        # print data['form']['tax_id']
        # if self.env.user.company_id.invoice_step == '1step':
        #     if data['form']['operating_unit_id']:
        #         operating_unit_id = self.env['operating.unit'].browse(data['form']['operating_unit_id'][0])
        #         if not data['form']['include_no_vat']:
        #             domain = [('type', 'in', ('out_invoice', 'out_refund')), ('number', '!=', False),
        #                       ('state', '!=', 'draft'), ('tax_id', '=', data['form']['tax_id'][0])]
        #         else:
        #             domain = [('type', 'in', ('out_invoice', 'out_refund')), ('number', '!=', False),
        #                       ('state', '!=', 'draft')]
        #
        #         domain.append(('date_invoice', '>=', data['form']['date_from']))
        #         domain.append(('date_invoice', '<=', data['form']['date_to']))
        #         domain.append(('operating_unit_id', '=', data['form']['operating_unit_id'][0]))
        #         docs = self.env['account.invoice'].search(domain, order='date_invoice,number asc')
        #     else:
        #         domain = [('type', 'in', ('out_invoice', 'out_refund')), ('number', '!=', False), ('state', '!=', 'draft'),('tax_id', '=', data['form']['tax_id'][0])]
        #         domain.append(('date_invoice', '>=', data['form']['date_from']))
        #         domain.append(('date_invoice', '<=', data['form']['date_to']))
        #         docs = self.env['account.invoice'].search(domain, order='date_invoice,number asc')
        # else:
        #
        #     if data['form']['operating_unit_id']:
        #         operating_unit_id = self.env['operating.unit'].browse(data['form']['operating_unit_id'][0])
        #         if not data['form']['include_no_vat']:
        #             domain = [('type', 'in', ('out_invoice', 'out_refund')), ('tax_inv_generated', '=', True),
        #                       ('tax_inv_no', '!=', False), ('tax_id', '=', data['form']['tax_id'][0])]
        #         else:
        #             domain = [('type', 'in', ('out_invoice', 'out_refund')), ('tax_inv_generated', '=', True),
        #                       ('tax_inv_no', '!=', False)]
        #
        #         domain.append(('tax_inv_date', '>=', data['form']['date_from']))
        #         domain.append(('tax_inv_date', '<=', data['form']['date_to']))
        #         domain.append(('operating_unit_id', '=', data['form']['operating_unit_id'][0]))
        #         docs = self.env['account.invoice'].search(domain, order='tax_inv_date,tax_inv_no asc')
        #
        #     else:
        #         if not data['form']['include_no_vat']:
        #             domain = [('type', 'in', ('out_invoice', 'out_refund')), ('tax_inv_generated', '=', True),
        #                       ('tax_inv_no', '!=', False),('tax_id', '=', data['form']['tax_id'][0])]
        #         else:
        #             domain = [('type', 'in', ('out_invoice', 'out_refund')), ('tax_inv_generated', '=', True),
        #                       ('tax_inv_no', '!=', False)]
        #
        #         domain.append(('tax_inv_date', '>=', data['form']['date_from']))
        #         domain.append(('tax_inv_date', '<=', data['form']['date_to']))
        #         docs = self.env['account.invoice'].search(domain, order='tax_inv_date,tax_inv_no asc')

        # print "DOCS"
        # print docs

        # print (operating_unit_id)
        docs = self.env['account.move.line'].search(domain, order='date asc')
        print ('-----DOCS--------')
        print (docs)

        return {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': docs,
            'company_id': company_id,
            'data': data,
        }



#start This is to generate purchase tax report
class report_purchase_tax_report(models.AbstractModel):
    _name = 'report.itaas_print_tax_report.purchase_tax_report_id'


    @api.model
    def _get_report_values(self, docids, data=None):
        company_id = self.env.user.company_id

        domain = [('account_id.purchase_tax_report','=',True),('date','>=',data['date_from']),('date','<=',data['date_to']),('move_id.state','=','posted')]
        #
        # if data['form']['tax_id']:
        #     account_id = self.env['account.tax'].browse(data['form']['tax_id'][0]).account_id
        #     domain.append(('account_id', '=', account_id.id))
        # if data['form']['date_from']:
        #     domain.append(('date', '>=', data['form']['date_from']))
        # if data['form']['date_to']:
        #     domain.append(('date', '<=', data['form']['date_to']))
        #
        #
        # if data['form']['operating_unit_id']:
        #     operating_unit_id = self.env['operating.unit'].browse(data['form']['operating_unit_id'][0])
        #     domain.append(('operating_unit_id', '=', data['form']['operating_unit_id'][0]))
        # else:
        #     operating_unit_id = False

        # print domain
        docs = self.env['account.move.line'].search(domain, order='date asc')
        # print docs

        return {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': docs,
            'company_id': company_id,
            'data': data,
        }
