# -*- coding: utf-8 -*-
# Copyright (C) 2016-2017  Technaureus Info Solutions(<http://technaureus.com/>).

from odoo import models, fields, api, _
from datetime import datetime
#from StringIO import StringIO
from io import BytesIO
import base64
from odoo.exceptions import UserError
from odoo.tools import misc
import xlwt
from decimal import *
from dateutil.relativedelta import relativedelta
import calendar
from io import StringIO


# class account_invoice(models.Model):
#     _inherit = 'account.invoice'
#
#     def get_total_amount_multi_currency(self, move_id):
#         total_amount = 0.0
#         for line in move_id.line_ids:
#             total_amount += abs(line.debit)
#
#         # print "total amount"
#         # print total_amount
#         return total_amount
#
#     def get_tax_amount_multi_currency(self, move_id):
#         tax_amount = 0.0
#         for line in move_id.line_ids:
#             if line.account_id.sale_tax_report:
#                 tax_amount += abs(line.balance)
#
#         #print "tax amount"
#         #print tax_amount
#         return tax_amount

#this is for tax report section
class tax_report(models.TransientModel):
    _name = 'tax.report'

    def _get_year(self):
        curr_date = datetime.now()
        last_year = curr_date.year - 1 + 543
        current_year = curr_date.year + 543
        next_year = curr_date.year + 1 + 543

        return [(last_year, last_year), (current_year, current_year), (next_year, next_year)]

    date_from = fields.Date(string='Date From',required=True)
    date_to = fields.Date(string='Date To',required=True)
    month = fields.Selection([
        ('1','มกราคม'),
        ('2','กุมภาพันธ์'),
        ('3', 'มีนาคม'),
        ('4', 'เมษายน'),
        ('5', 'พฤษภาคม'),
        ('6', 'มิถุนายน'),
        ('7', 'กรกฏาคม'),
        ('8', 'สิงหาคม'),
        ('9', 'กันยายน'),
        ('10', 'ตุลาคม'),
        ('11', 'พฤศจิกายน'),
        ('12', 'ธันวาคม'),
    ],string='Month',required=True)
    year = fields.Integer(string='Year')
    report_type = fields.Selection([('sale','ภาษีขาย'),('purchase','ภาษีซื้อ')],default='sale',string='Report Type', required=True)
    #partner_id = fields.Many2one('res.partner', string='Partner')
    tax_id = fields.Many2one('account.tax', string='Tax Type',required=False)
    # disable_excel_tax_report = fields.Boolean(string="Disable Tax Report in Excel Format")
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit')
    company_id = fields.Many2one('res.company')
    include_no_vat = fields.Boolean(string='Include No Vat')


    
    @api.model
    def default_get(self, fields):
        res = super(tax_report,self).default_get(fields)
        curr_date = datetime.now()
        from_date = datetime(curr_date.year,curr_date.month,1).date() or False
        to_date = datetime(curr_date.year,curr_date.month,calendar.monthrange(curr_date.year, curr_date.month)[1]).date() or False
        year = curr_date.year + 543
        # disable_excel_tax_report = self.env.user.company_id.disable_excel_tax_report
        company_id = self.env.user.company_id.id
        res.update({'year': year,'month':str(curr_date.month),'date_from': str(from_date), 'date_to': str(to_date),'company_id': company_id,})
        print ('default get')
        print (res)
        return res

    @api.onchange('month','year')
    def onchange_month_year(self):
        if self.month and self.year:
            select_month = self.month
            select_year = self.year - 543
            month_day = calendar.monthrange(select_year, int(select_month))[1]
            from_date = datetime(select_year, int(select_month), 1).date() or False
            to_date = datetime(select_year, int(select_month), month_day).date() or False
            self.date_from = from_date
            self.date_to = to_date

    @api.onchange('report_type')
    def onchange_report_type(self):
        result = {}
        if self.report_type == 'sale':
            self.tax_id = self.env['account.tax'].search([('type_tax_use','=','sale'),('company_id','=',self.company_id.id),('tax_report','=',True)],limit=1)
            result['domain'] = {'tax_id': [('type_tax_use','=','sale'),('wht','=',False)]}
        if self.report_type == 'purchase':
            self.tax_id = self.env['account.tax'].search(
                [('type_tax_use', '=', 'purchase'), ('company_id', '=', self.company_id.id), ('tax_report', '=', True)],
                limit=1)
            result['domain'] = {'tax_id': [('type_tax_use','=','purchase'),('wht','=',False)]}

        return result

    # def generate_report(self):
    #     data = {'date_start': self.start_date, 'date_stop': self.end_date, 'config_ids': self.pos_config_ids.ids}
    #     return self.env.ref('point_of_sale.sale_details_report').report_action([], data=data)

    def print_report_pdf(self):
        data = {'date_from': self.date_from, 'date_to': self.date_to, 'report_type': self.report_type, 'tax_id': self.tax_id, 'company_id': self.company_id}
        # data['form'] = self.read(['date_from', 'date_to', 'report_type', 'tax_id', 'operating_unit_id','company_id','include_no_vat'])[0]
        # print ('------DATA---')
        # print (data)
        if data['report_type'] == 'sale':
            # return self.env['report'].get_action(self, 'thai_accounting.sale_tax_report_id', data=data)
            return self.env.ref('itaas_print_tax_report.action_sale_tax_report_id').report_action([], data=data)
        else:
            # return self.env['report'].get_action(self, 'thai_accounting.purchase_tax_report_id', data=data)
            return self.env.ref('itaas_print_tax_report.action_purchase_tax_report_id').report_action([], data=data)


    def get_amount_multi_currency(self,move_id):
        total_amount = 0.0
        tax_amount = 0.0
        for line in move_id.line_ids:
            total_amount += abs(line.debit)
            if line.account_id.sale_tax_report:
                tax_amount += abs(line.balance)

        return total_amount,tax_amount




    # @api.multi
    def print_report(self):
        # fl = StringIO()
        fl = BytesIO()
        company_id = self.env.user.company_id
        # ir_values = self.env['ir.values']
        IrDefault = self.env['ir.default']
        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet('Sheet 1')
        font = xlwt.Font()
        font.bold = True
        font.bold = True
        for_right = xlwt.easyxf("font: name  Times New Roman,color black,  height 180;  align: horiz right,vertical center; borders: top thin, bottom thin, left thin, right thin")
        for_right.num_format_str = '#,###.00'
        for_right_bold = xlwt.easyxf("font: bold 1, name  Times New Roman,color black,  height 180;  align: horiz right,vertical center; borders: top thin, bottom thin, left thin, right thin")
        for_right_bold.num_format_str = '#,###.00'
        for_center = xlwt.easyxf("font: name  Times New Roman, color black,  height 180; align: horiz center,vertical center,wrap on; borders: top thin, bottom thin, left thin, right thin")
        for_left = xlwt.easyxf("font: name  Times New Roman,color black,  height 180;  align: horiz left,vertical center; borders: top thin, bottom thin, left thin, right thin")
        for_center_bold = xlwt.easyxf("font: bold 1, name  Times New Roman, color black, height 180;  align: horiz center,vertical center,wrap on; borders: top thin, bottom thin, left thin, right thin")
        for_left_bold_no_border = xlwt.easyxf("font: bold 1, name  Times New Roman, color black, height 180;  align: horiz left,vertical center;")
        
        GREEN_TABLE_HEADER = xlwt.easyxf(
                 'font: bold 1, name  Times New Roman, height 300,color black;'
                 'align: vertical center, horizontal center, wrap on;'
                    'borders: top thin, bottom thin, left thin, right thin;'
                 'pattern:  pattern_fore_colour white, pattern_back_colour white'
                 )
        
        alignment = xlwt.Alignment()  # Create Alignment
        alignment.horz = xlwt.Alignment.HORZ_RIGHT
        style = xlwt.easyxf('align: wrap yes')
        style.num_format_str = '#,###.00'
        cr, uid , context=self.env.args

        if self.operating_unit_id:
            operating_unit_id = self.operating_unit_id
            company = self.operating_unit_id.company_id and operating_unit_id.partner_id.name or ''
            company_branch = operating_unit_id.partner_id and operating_unit_id.partner_id.name or ''
            company_address = ''
            if operating_unit_id.partner_id.street:
                company_address += operating_unit_id.partner_id.street + " "
            if operating_unit_id.partner_id.street2:
                company_address += operating_unit_id.partner_id.street2 + " "
            if operating_unit_id.partner_id.sub_district_id.name:
                if operating_unit_id.partner_id.state_id.code == 'BKK':
                    company_address += "แขวง" + operating_unit_id.partner_id.sub_district_id.name + " "
                else:
                    company_address += "ต." + operating_unit_id.partner_id.sub_district_id.name + " "
            if operating_unit_id.partner_id.district_id.name:
                if operating_unit_id.partner_id.state_id.code == 'BKK':
                    company_address += "เขต" + operating_unit_id.partner_id.district_id.name + " "
                else:
                    company_address += "อ." + operating_unit_id.partner_id.district_id.name + " "
            if operating_unit_id.partner_id.state_id:
                if operating_unit_id.partner_id.state_id.code == 'BKK':
                    company_address += operating_unit_id.partner_id.state_id.name + " "
                else:
                    company_address += "จ." + operating_unit_id.partner_id.state_id.name + " "
            if operating_unit_id.partner_id.zip:
                company_address += operating_unit_id.partner_id.zip + " "
            tax_id = operating_unit_id.partner_id.vat or ''
            branch_no = operating_unit_id.partner_id.branch_no or ''
        else:
            user = self.env['res.users'].browse(uid)
            company = user.company_id and user.company_id.name or ''
            company_branch = user.company_id and user.company_id.name or ''
            company_address = user.company_id and user.company_id.get_company_full_address() or ''
            tax_id = user.company_id and user.company_id.vat or ''
            branch_no = user.company_id and user.company_id.branch_no or ''

        taxes_id = IrDefault.sudo().get('product.template', 'taxes_id', company_id=self.company_id.id)
        supplier_taxes_id = IrDefault.sudo().get('product.template', 'supplier_taxes_id',company_id=self.company_id.id)

        t_id = self.env['account.tax'].browse(taxes_id)
        s_id = self.env['account.tax'].browse(supplier_taxes_id)
        
        if self.report_type == 'sale':
            worksheet.row(0).height = 200
            worksheet.col(0).width = 2000
            worksheet.col(1).width = 4000
            worksheet.col(2).width = 3500
            worksheet.col(3).width = 6000
            worksheet.col(4).width = 6000
            worksheet.col(5).width = 3000
            worksheet.col(6).width = 2000
            worksheet.col(7).width = 3000
            worksheet.col(8).width = 3000

        if self.report_type == 'purchase':
            worksheet.row(0).height = 200
            worksheet.col(0).width = 2000
            worksheet.col(1).width = 4000
            worksheet.col(2).width = 3500
            worksheet.col(3).width = 6000
            worksheet.col(4).width = 6000
            worksheet.col(5).width = 3000
            worksheet.col(6).width = 2000
            worksheet.col(7).width = 3000
            worksheet.col(8).width = 3000
        
        borders = xlwt.Borders()
        borders.bottom = xlwt.Borders.MEDIUM
        border_style = xlwt.XFStyle()  # Create Style
        border_style.borders = borders
        
        inv_row = 11
        year = int(datetime.strptime(self.date_from, '%Y-%m-%d').strftime('%Y'))
        year += 543

        month = int(datetime.strptime(self.date_from, '%Y-%m-%d').strftime('%m'))
        if month == 1:
            monthth = 'มกราคม'
        elif month == 2:
            monthth = 'กุมภาพันธ์'
        elif month == 3:
            monthth = 'มีนาคม'
        elif month == 3:
            monthth = 'มีนาคม'
        elif month == 4:
            monthth = 'เมษายน'
        elif month == 5:
            monthth = 'พฤษภาคม'
        elif month == 6:
            monthth = 'มิถุนายน'
        elif month == 7:
            monthth = 'กรกฏาคม'
        elif month == 8:
            monthth = 'สิงหาคม'
        elif month == 9:
            monthth = 'กันยายน'
        elif month == 10:
            monthth = 'ตุลาคม'
        elif month == 11:
            monthth = 'พฤศจิกายน'
        else:
            monthth = 'ธันวาคม'


        #option 2, generate tax report from account.invoice
        # this is first option to get all customer tax invoice from "account.invoice" with "sale tax account"
        inv_row_merge_head = inv_row + 1
        # sale
        customer_invoice_obj = self.env['account.invoice']
        # purchase
        invoice_obj = self.env['account.move.line']

        if self.report_type == 'sale':

            # print t_id
            if self.tax_id.tax_report:
                worksheet.write_merge(0, 1, 0, 8, "รายงานภาษีขาย", GREEN_TABLE_HEADER)
            else:
                worksheet.write_merge(0, 1, 0, 8, "รายงานภาษีขายยังไม่ถึงกำหนด", GREEN_TABLE_HEADER)

            worksheet.write(3, 1, 'เดือนภาษี', for_left_bold_no_border)
            worksheet.write(3, 2, monthth, for_left_bold_no_border)
            worksheet.write(3, 4, 'ปี', for_left_bold_no_border)
            worksheet.write(3, 5, year, for_left_bold_no_border)

            worksheet.write(5, 1, 'ชื่อผู้ประกอบการ', for_left_bold_no_border)
            worksheet.write(5, 2, company, for_left_bold_no_border)
            worksheet.write(5, 4, 'เลขประจำผู้เสียภาษีอากร', for_left_bold_no_border)
            worksheet.write(5, 5, tax_id, for_left_bold_no_border)

            worksheet.write(7, 1, 'ชื่อสถานประกอบการ', for_left_bold_no_border)
            worksheet.write(7, 2, company_branch, for_left_bold_no_border)
            worksheet.write(7, 4, 'สำนักงานใหญ่ / สาขา', for_left_bold_no_border)
            worksheet.write(7, 5, branch_no, for_left_bold_no_border)

            worksheet.write(9, 1, 'สถานประกอบการ', for_left_bold_no_border)
            worksheet.write(9, 2, company_address, for_left_bold_no_border)
            worksheet.write(9, 4, 'หน้าที่', for_left_bold_no_border)
            # worksheet.write(9, 5, branch_no, for_left_bold_no_border)


            worksheet.write_merge(inv_row, inv_row_merge_head, 0, 0, "ลำดับที่", for_center_bold)
            worksheet.write_merge(inv_row, inv_row, 1, 2, "ใบกำกับภาษี", for_center_bold)
            worksheet.write(inv_row_merge_head, 1, 'วัน เดือน ปี', for_center_bold)
            worksheet.write(inv_row_merge_head, 2, 'เลขที่', for_center_bold)
            worksheet.write_merge(inv_row, inv_row_merge_head, 3, 3, "ชื่อผู้ซื้อสินค้า/ผู้รับบริการ",
                                  for_center_bold)
            worksheet.write_merge(inv_row, inv_row_merge_head, 4, 4,
                                  'เลขประจำตัวผู้เสียภาษีอากรของผู้ซื้อสินค้า/ผู้รับบริการ', for_center_bold)
            worksheet.write_merge(inv_row, inv_row, 5, 6, "สถานประกอบการ", for_center_bold)
            worksheet.write(inv_row_merge_head, 5, 'สำนักงานใหญ่', for_center_bold)
            worksheet.write(inv_row_merge_head, 6, 'สาขาที่', for_center_bold)
            worksheet.write_merge(inv_row, inv_row_merge_head, 7, 7, "มูลค่าสินค้าหรือบริการ", for_center_bold)
            worksheet.write_merge(inv_row, inv_row_merge_head, 8, 8, "จำนวนเงินภาษีมูลค่าเพิ่ม",
                                  for_center_bold)
            # worksheet.write_merge(inv_row, inv_row_merge_head, 9, 9, "จำนวนเงินรวม",
            #                       for_center_bold)

            if self.env.user.company_id.invoice_step == '1step':
                if not self.include_no_vat:
                    domain = [('type', 'in', ('out_invoice', 'out_refund')),('number', '!=', False),('state', '!=', 'draft'),('tax_id', '=', self.tax_id.id)]
                else:
                    domain = [('type', 'in', ('out_invoice', 'out_refund')),('number', '!=', False),('state', '!=', 'draft')]

                domain.append(('date_invoice', '>=', self.date_from))
                domain.append(('date_invoice', '<=', self.date_to))
            else:
                if not self.include_no_vat:
                    domain = [('type','in',('out_invoice','out_refund')),('tax_inv_generated','=',True),('tax_inv_no','!=',False),('tax_id', '=', self.tax_id.id)]
                else:
                    domain = [('type','in',('out_invoice','out_refund')),('tax_inv_generated','=',True),('tax_inv_no','!=',False)]

                domain.append(('tax_inv_date', '>=', self.date_from))
                domain.append(('tax_inv_date', '<=', self.date_to))

            if self.operating_unit_id:
                domain.append(('operating_unit_id', '=', self.operating_unit_id.id))

            # if self.partner_id:
            #    domain.append(('partner_id','=',self.partner_id[0].id))
            inv_row += 1

            #order by tax_inv_date or date_invoice
            if self.env.user.company_id.invoice_step == '1step':
                invoices = customer_invoice_obj.search(domain, order='date_invoice,number asc')
            else:
                invoices = customer_invoice_obj.search(domain, order='tax_inv_date,tax_inv_no asc')

            if invoices:
                sl_no = 1
                untaxed_total = tax_total = 0.0
                for inv in invoices:
                    inv_row += 1

                    if inv.date_invoice and self.env.user.company_id.invoice_step == '1step':
                        tax_inv_date = datetime.strptime(inv.date_invoice, '%Y-%m-%d').strftime('%d/%m/%Y')
                    else:
                        tax_inv_date = datetime.strptime(inv.tax_inv_date, '%Y-%m-%d').strftime('%d/%m/%Y')

                    worksheet.write(inv_row, 0, sl_no, for_center)
                    worksheet.write(inv_row, 1, tax_inv_date, for_center)

                    if inv.number and self.env.user.company_id.invoice_step == '1step':
                        worksheet.write(inv_row, 2, inv.number, for_center)
                    else:
                        worksheet.write(inv_row, 2, inv.tax_inv_no, for_center)

                    if inv.partner_id.parent_id:
                        worksheet.write(inv_row, 3, inv.partner_id.parent_id.name, for_left)
                        worksheet.write(inv_row, 4, inv.partner_id.parent_id.vat, for_left)
                    else:
                        worksheet.write(inv_row, 3, inv.partner_id.name, for_left)
                        worksheet.write(inv_row, 4, inv.partner_id.vat, for_left)

                    if inv.operating_unit_id:
                        is_branch_no = inv.operating_unit_id.partner_id.branch_no
                    else:
                        is_branch_no = inv.partner_id.branch_no

                    if int(is_branch_no):
                        worksheet.write(inv_row, 5, ' ', for_left)
                        worksheet.write(inv_row, 6, is_branch_no, for_left)
                    else:
                        worksheet.write(inv_row, 5, is_branch_no, for_left)
                        worksheet.write(inv_row, 6, ' ', for_left)

                    if inv.state in ('open', 'paid'):
                        # print "check by INV"
                        # print inv.currency_id.id
                        # print self.env.user.company_id.currency_id.id

                        if inv.currency_id.id != self.env.user.company_id.currency_id.id:
                            # print "MULTI CURRENCY"
                            if inv.type == 'out_invoice' and not inv.adjust_move_id:
                                # print "MULTI CURRENCY-1"
                                tatal_amount,tax_amount = self.get_amount_multi_currency(inv.move_id)
                                untaxed_amount = tatal_amount-tax_amount
                                worksheet.write(inv_row, 7, untaxed_amount, for_right)
                                worksheet.write(inv_row, 8, tax_amount, for_right)
                                untaxed_total += untaxed_amount
                                tax_total += tax_amount
                            elif inv.type == 'out_invoice' and inv.adjust_move_id:
                                # print "MULTI CURRENCY-2"
                                ######## first move id will get correct total amount, but tax is 0
                                ####### second move id will get correct tax amount
                                tatal_amount_1, tax_amount_1 = self.get_amount_multi_currency(inv.move_id)
                                tatal_amount_2, tax_amount_2 = self.get_amount_multi_currency(inv.adjust_move_id)
                                untaxed_amount = tatal_amount_1 - tax_amount_2

                                worksheet.write(inv_row, 7, untaxed_amount, for_right)
                                worksheet.write(inv_row, 8, tax_amount_2, for_right)
                                # worksheet.write(inv_row, 9, inv.amount_untaxed + inv.amount_tax, for_right)
                                untaxed_total += untaxed_amount
                                tax_total += tax_amount_2

                            elif inv.type == 'out_refund' and not inv.adjust_move_id:
                                tatal_amount, tax_amount = self.get_amount_multi_currency(inv.move_id)
                                untaxed_amount = tatal_amount - tax_amount
                                worksheet.write(inv_row, 7, untaxed_amount* (-1), for_right)
                                worksheet.write(inv_row, 8, tax_amount* (-1), for_right)
                                untaxed_total += untaxed_amount* (-1)
                                tax_total += tax_amount* (-1)

                            elif inv.type == 'out_refund' and inv.adjust_move_id:
                                tatal_amount_1, tax_amount_1 = self.get_amount_multi_currency(inv.move_id)
                                tatal_amount_2, tax_amount_2 = self.get_amount_multi_currency(inv.adjust_move_id)
                                untaxed_amount = tatal_amount_1 - tax_amount_2

                                worksheet.write(inv_row, 7, untaxed_amount * (-1), for_right)
                                worksheet.write(inv_row, 8, tax_amount_2 * (-1), for_right)
                                # worksheet.write(inv_row, 9, inv.amount_untaxed + inv.amount_tax, for_right)
                                untaxed_total += untaxed_amount * (-1)
                                tax_total += tax_amount_2 * (-1)
                        else:
                            ##########same currency THB#####
                            #print "SAME CURRENCY"
                            if inv.type == 'out_invoice':
                                worksheet.write(inv_row, 7, inv.amount_untaxed, for_right)
                                worksheet.write(inv_row, 8, inv.amount_tax, for_right)
                                # worksheet.write(inv_row, 9, inv.amount_untaxed + inv.amount_tax, for_right)
                                untaxed_total += inv.amount_untaxed
                                tax_total += inv.amount_tax
                            else:
                                worksheet.write(inv_row, 7, (inv.amount_untaxed) * (-1), for_right)
                                worksheet.write(inv_row, 8, (inv.amount_tax) * (-1), for_right)
                                # worksheet.write(inv_row, 9, (inv.amount_untaxed) * (-1) + (inv.amount_tax) * (-1), for_right)
                                untaxed_total += (inv.amount_untaxed)*(-1)
                                tax_total += (inv.amount_tax) * (-1)

                    if inv.state == 'cancel':
                        worksheet.write(inv_row, 7, ".00", for_right)
                        worksheet.write(inv_row, 8, ".00", for_right)
                        # worksheet.write(inv_row, 9, "0", for_right)

                    sl_no += 1

                inv_row += 1
                worksheet.write(inv_row, 6, 'Total', for_center_bold)
                worksheet.write(inv_row, 7, untaxed_total, for_right_bold)
                worksheet.write(inv_row, 8, tax_total, for_right_bold)
                # worksheet.write(inv_row, 9, untaxed_total + tax_total, for_right_bold)
            else:
                raise UserError(_('There is invoices between this date range.'))

        if self.report_type == 'purchase':
            if self.tax_id.tax_report:
                worksheet.write_merge(0, 1, 0, 8, "รายงานภาษีซื้อ", GREEN_TABLE_HEADER)
            else:
                worksheet.write_merge(0, 1, 0, 8, "รายงานภาษีซื้อยังไม่ถึงกำหนด", GREEN_TABLE_HEADER)

            worksheet.write(3, 1, 'เดือนภาษี', for_left_bold_no_border)
            worksheet.write(3, 2, monthth, for_left_bold_no_border)
            worksheet.write(3, 4, 'ปี', for_left_bold_no_border)
            worksheet.write(3, 5, year, for_left_bold_no_border)

            worksheet.write(5, 1, 'ชื่อผู้ประกอบการ', for_left_bold_no_border)
            worksheet.write(5, 2, company, for_left_bold_no_border)
            worksheet.write(5, 4, 'เลขประจำผู้เสียภาษีอากร', for_left_bold_no_border)
            worksheet.write(5, 5, tax_id, for_left_bold_no_border)

            worksheet.write(7, 1, 'ชื่อสถานประกอบการ', for_left_bold_no_border)
            worksheet.write(7, 2, company_branch, for_left_bold_no_border)
            worksheet.write(7, 4, 'สำนักงานใหญ่ / สาขา', for_left_bold_no_border)
            worksheet.write(7, 5, branch_no, for_left_bold_no_border)

            worksheet.write(9, 1, 'สถานประกอบการ', for_left_bold_no_border)
            worksheet.write(9, 2, company_address, for_left_bold_no_border)

            worksheet.write_merge(inv_row, inv_row_merge_head, 0, 0, "ลำดับที่", for_center_bold)
            worksheet.write_merge(inv_row, inv_row, 1, 2, "ใบกำกับภาษี", for_center_bold)
            worksheet.write(inv_row_merge_head, 1, 'วัน เดือน ปี', for_center_bold)
            worksheet.write(inv_row_merge_head, 2, 'เลขที่', for_center_bold)
            worksheet.write_merge(inv_row, inv_row_merge_head, 3, 3, "ชื่อผู้ขายสินค้า/ผู้ให้บริการ", for_center_bold)
            worksheet.write_merge(inv_row, inv_row_merge_head, 4, 4,
                                  'เลขประจำตัวผู้เสียภาษีอากรของผู้ขายสินค้า/ผู้ให้บริการ', for_center_bold)
            worksheet.write_merge(inv_row, inv_row, 5, 6, "สถานประกอบการ", for_center_bold)
            worksheet.write(inv_row_merge_head, 5, 'สำนักงานใหญ่', for_center_bold)
            worksheet.write(inv_row_merge_head, 6, 'สาขาที่', for_center_bold)
            worksheet.write_merge(inv_row, inv_row_merge_head, 7, 7, "มูลค่าสินค้าหรือบริการ", for_center_bold)
            worksheet.write_merge(inv_row, inv_row_merge_head, 8, 8, "จำนวนเงินภาษีมูลค่าเพิ่ม", for_center_bold)
            # worksheet.write_merge(inv_row, inv_row_merge_head, 9, 9, "จำนวนเงินรวม", for_center_bold)

            domain = [('account_id', '=', self.tax_id[0].account_id.id),('is_closing_month','=',False)]
            if self.date_from:
                domain.append(('date', '>=', self.date_from))
            if self.date_to:
                domain.append(('date', '<=', self.date_to))

            if self.operating_unit_id:
                domain.append(('operating_unit_id', '=', self.operating_unit_id.id))

            inv_row += 1
            print('Execl Domain' + str(domain))
            invoices = invoice_obj.search(domain,order='invoice_date asc')
            if invoices:
                sl_no = 1
                untaxed_total = tax_total = 0.0
                amount_tax = 0.0
                amount_untax = 0.0
                for inv in invoices:
                    inv_row += 1
                    worksheet.write(inv_row, 0, sl_no, for_center)
                    if inv.invoice_date:
                        worksheet.write(inv_row, 1, datetime.strptime(inv.invoice_date, '%Y-%m-%d').strftime('%d/%m/%Y'), for_center)
                    else:
                        worksheet.write(inv_row, 1, datetime.strptime(inv.date, '%Y-%m-%d').strftime('%d/%m/%Y'),for_center)

                    worksheet.write(inv_row, 2, inv.ref, for_left)
                    if inv.partner_id:
                        worksheet.write(inv_row, 3, inv.partner_id.name, for_left)
                        worksheet.write(inv_row, 4, inv.partner_id.vat, for_left)
                    else:
                        worksheet.write(inv_row, 3, inv.move_id.supplier_name_text, for_left)
                        worksheet.write(inv_row, 4, inv.move_id.supplier_taxid_text, for_left)

                    if inv.invoice_id:
                        is_branch_no = inv.invoice_id.operating_unit_id.partner_id.branch_no
                    else:
                        if inv.partner_id:
                            is_branch_no = inv.partner_id.branch_no
                        else:
                            is_branch_no = inv.move_id.supplier_branch_text

                    if int(is_branch_no):
                        worksheet.write(inv_row, 5, ' ', for_left)
                        worksheet.write(inv_row, 6, is_branch_no, for_left)
                    else:
                        worksheet.write(inv_row, 5, is_branch_no, for_left)
                        worksheet.write(inv_row, 6, ' ', for_left)

                    if inv.debit:
                        amount_tax = inv.debit
                    elif inv.credit:
                        amount_tax = inv.credit * (-1)
                    else:
                        amount_tax = 0

                    if inv.amount_before_tax:
                        # print "1"
                        amount_untax = inv.amount_before_tax
                    elif inv.invoice_id and inv.invoice_id.amount_untaxed:
                        # print "2"
                        amount_untax = inv.invoice_id.amount_untaxed
                    else:
                        # print "3"
                        amount_untax = amount_tax*100/7

                    # amount_untax = amount_tax*100/7

                    worksheet.write(inv_row, 7, amount_untax, for_right)
                    worksheet.write(inv_row, 8, amount_tax, for_right)
                    # worksheet.write(inv_row, 9, amount_untax + amount_tax, for_right)
                    sl_no += 1
                    untaxed_total += amount_untax
                    tax_total += amount_tax

                inv_row += 1
                worksheet.write(inv_row, 6, 'Total', for_center_bold)
                worksheet.write(inv_row, 7, untaxed_total, for_right_bold)
                worksheet.write(inv_row, 8, tax_total, for_right_bold)
                # worksheet.write(inv_row, 9, untaxed_total + tax_total, for_right_bold)
            else:
                raise UserError(_('There is no invoices between this date range.'))

        workbook.save(fl)
        fl.seek(0)
        
        buf = base64.encodestring(fl.read())
        cr, uid, context = self.env.args
        ctx = dict(context)
        ctx.update({'report_file': buf})
        self.env.args = cr, uid, misc.frozendict(context)
        ## To remove those previous saved report data from table. To avoid unwanted storage
        self._cr.execute("TRUNCATE tax_excel_export CASCADE")
        wizard_id = self.env['tax.excel.export'].create(vals={'name': 'Tax Report.xls','report_file': ctx['report_file']})
        return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'tax.excel.export',
                'target': 'new',
                'context': ctx,
                'res_id': wizard_id.id,
        }


class tax_excel_export(models.TransientModel):
    _name = 'tax.excel.export'

    report_file = fields.Binary('File')
    name = fields.Char(string='File Name', size=32)

    # @api.model
    # def create(self, vals):
    #     print vals
    #     return super(tax_excel_export, self).create(vals)

    # @api.multi
    def action_back(self):
        if self._context is None:
            self._context = {}
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'tax.report',
            'target': 'new',
        }


class pnd53_report(models.TransientModel):
    _name = 'pnd53.report'
    date_from = fields.Date(string='Date From',required=True)
    date_to = fields.Date(string='Date To',required=True)
    report_type = fields.Selection([('personal', 'ภงด3'), ('company', 'ภงด53')],string='Report Type', required=True)
    month = fields.Char(string='Month')
    company_id = fields.Many2one('res.company')

    @api.model
    def default_get(self, fields):
        res = super(pnd53_report, self).default_get(fields)
        curr_date = datetime.now()
        from_date = datetime(curr_date.year, curr_date.month, 1).date() or False
        to_date = datetime(curr_date.year, curr_date.month, curr_date.day).date() or False
        res.update({'date_from': str(from_date), 'date_to': str(to_date)})
        return res

    def print_pnd53_report(self):
        print('bbbbbbbbbbb')
        # data = {}
        data = {'date_from': self.date_from, 'date_to': self.date_to, 'report_type': self.report_type,
                'month': self.month, 'company_id': self.company_id}
        # data['form'] = self.read(['date_from', 'date_to', 'report_type', 'month','company_id'])[0]

        if data['report_type'] == 'company':
            # return self.env['report'].get_action(self, 'thai_accounting.report_pnd53_id', data=data)
            return self.env.ref('itaas_print_tax_report.action_report_pnd53_id').report_action(self, data=data)
        elif data['report_type'] == 'personal':
            print('kuyyyyyyyyyyyyyyy')
            # return self.env['report'].get_action(self, 'thai_accounting.report_pnd3_id', data=data)
            return self.env.ref('itaas_print_tax_report.action_report_pnd3_id').report_action(self, data=data)
        else:
            # return self.env['report'].get_action(self, 'thai_accounting.report_pnd2_id', data=data)
            return self.env.ref('itaas_print_tax_report.action_report_pnd2_id').report_action(self, data=data)

    # @api.multi
    def print_pnd53_report_to_text(self):

        context = dict(self._context or {})
        file_type = context.get('file')

        fl = StringIO()
        workbook = xlwt.Workbook(encoding='utf-8')

        font = xlwt.Font()
        font.bold = True
        font.bold = True
        for_right = xlwt.easyxf(
            "font: name  Times New Roman,color black,  height 180;  align: horiz right,vertical center; borders: top thin, bottom thin, left thin, right thin")
        for_right.num_format_str = '#,###.00'
        for_right_bold = xlwt.easyxf(
            "font: bold 1, name  Times New Roman,color black,  height 180;  align: horiz right,vertical center; borders: top thin, bottom thin, left thin, right thin")
        for_right_bold.num_format_str = '#,###.00'
        for_center = xlwt.easyxf(
            "font: name  Times New Roman, color black,  height 180; align: horiz center,vertical center,wrap on; borders: top thin, bottom thin, left thin, right thin")
        for_left = xlwt.easyxf(
            "font: name  Times New Roman,color black,  height 180;  align: horiz left,vertical center; borders: top thin, bottom thin, left thin, right thin")
        for_center_bold = xlwt.easyxf(
            "font: bold 1, name  Times New Roman, color black, height 180;  align: horiz center,vertical center,wrap on; borders: top thin, bottom thin, left thin, right thin")
        for_left_bold_no_border = xlwt.easyxf(
            "font: bold 1, name  Times New Roman, color black, height 180;  align: horiz left,vertical center;")

        GREEN_TABLE_HEADER = xlwt.easyxf(
            'font: bold 1, name  Times New Roman, height 300,color black;'
            'align: vertical center, horizontal center, wrap on;'
            'borders: top thin, bottom thin, left thin, right thin;'
            'pattern:  pattern_fore_colour white, pattern_back_colour white'
        )

        alignment = xlwt.Alignment()  # Create Alignment
        alignment.horz = xlwt.Alignment.HORZ_RIGHT
        style = xlwt.easyxf('align: wrap yes')
        style.num_format_str = '#,###.00'
        # cr, uid, context = self.env.args
        final_text = ""
        final_text_body = ""

        # -------------------------------------- PND 3 ----------------------------------------
        if self.report_type == 'personal':

            # worksheet = workbook.add_sheet('report')
            # worksheet_detail = workbook.add_sheet('report_detail')

            move_line_ids = self.env['account.move.line'].search(
                [('date_maturity', '>=', self.date_from), ('date_maturity', '<=', self.date_to),
                 ('wht_type.name', '=', 'personal'), ('wht_tax', '!=', False), ('account_id.wht', '=', True)],
                order='date_maturity ASC')
            move_ids = ""
            inv_row = 1
            for move in move_line_ids:
                move_ids += str(inv_row) + '|'
                move_ids += str(move.partner_id.vat) + '|'

                name_temp = move.partner_id.name.split(' ')

                if len(name_temp) >= 3:
                    title_name = name_temp[0]
                    first_name = name_temp[1]
                    last_name = name_temp[2]
                elif len(name_temp) == 2:
                    title_name = name_temp[0]
                    first_name = name_temp[1]
                    last_name = " "
                else:
                    title_name = " "
                    first_name = name_temp[0]
                    last_name = " "

                move_ids += str(title_name) + '|'
                move_ids += str(first_name) + '|'
                move_ids += str(last_name) + '|'

                if move.partner_id.street:
                    move_ids += str(move.partner_id.street)[0:30] + '|'
                else:
                    move_ids += '|'
                if move.partner_id.street2:
                    move_ids += str(move.partner_id.street2)[0:30] + '|'
                else:
                    move_ids += '|'
                if move.partner_id.city:
                    move_ids += str(move.partner_id.city)[0:30] + '|'
                else:
                    move_ids += '|'
                if move.partner_id.state_id and move.partner_id.state_id.name:
                    move_ids += str(move.partner_id.state_id.name)[0:40] + '|'
                else:
                    move_ids += '|'
                if move.partner_id.zip:
                    move_ids += str(move.partner_id.zip)[0:5] + '|'
                else:
                    move_ids += '|'

                if move.date_maturity:
                    # date = datetime.strptime(move.date_maturity, "%Y-%m-%d").date()
                    date = move.date_maturity
                    if len(str(date.day)) < 2:
                        day = '0' + str(date.day)
                    else:
                        day = str(date.day)
                    if len(str(date.month)) < 2:
                        month = '0' + str(date.month)
                    else:
                        month = str(date.month)
                    date_payment = day + '/' + month + '/' + str(date.year + 543)
                if date_payment:
                    move_ids += date_payment + '|'
                else:
                    move_ids += '|'
                # move_ids += strToDate(move.date_maturity).strftime("%d/%m/%Y") + '|'
                move_ids += str(move.name) + '|'

                if move.wht_type:
                    wht_type = str(move.wht_tax.amount)[0]
                    # if str(move.wht_tax.amount) == '1%':
                    #     wht_type = '1'
                    # elif move.wht_type == '2%':
                    #     wht_type = '2'
                    # elif move.wht_type == '3%':
                    #     wht_type = '3'
                    # elif move.wht_type == '5%':
                    #     wht_type = '5'

                move_ids += str(wht_type) + '|'
                move_ids += str(move.amount_before_tax) + '|'
                move_ids += str(move.credit) + '|'

                if inv_row != len(move_line_ids):
                    move_ids += '1' + "\n"
                else:
                    move_ids += '1'

                # worksheet.write(inv_row, 0, move_ids, for_left)
                final_text = final_text_body + str(move_ids)

                inv_row += 1


        # ------------------------------------ End PND 3 -------------------------------------------------

        # -------------------------------------- PND 53 ----------------------------------------
        elif self.report_type == 'company':

            # worksheet = workbook.add_sheet('report')
            # worksheet_detail = workbook.add_sheet('report_detail')

            move_line_ids = self.env['account.move.line'].search(
                [('date_maturity', '>=', self.date_from), ('date_maturity', '<=', self.date_to),
                 ('wht_type.name', '=', 'company'), ('wht_tax', '!=', False), ('account_id.wht', '=', True)],
                order='date_maturity,wht_reference ASC')
            move_ids = ""
            inv_row = 1
            for move in move_line_ids:
                move_ids += str(inv_row) + '|'
                move_ids += str(move.partner_id.vat)[0:13] + '|'
                move_ids += 'บริษัท' + '|'
                move_ids += str(move.partner_id.name)[0:160] + '|'

                if move.partner_id.street:
                    move_ids += str(move.partner_id.street)[0:30] + '|'
                else:
                    move_ids += '|'
                if move.partner_id.street2:
                    move_ids += str(move.partner_id.street2)[0:30] + '|'
                else:
                    move_ids += '|'
                if move.partner_id.city:
                    move_ids += str(move.partner_id.city)[0:30] + '|'
                else:
                    move_ids += '|'
                if move.partner_id.state_id and move.partner_id.state_id.name:
                    move_ids += str(move.partner_id.state_id.name)[0:40] + '|'
                else:
                    move_ids += '|'
                if move.partner_id.zip:
                    move_ids += str(move.partner_id.zip)[0:5] + '|'
                else:
                    move_ids += '|'

                if move.date_maturity:
                    # date = datetime.strptime(move.date_maturity, "%Y-%m-%d").date()
                    date = move.date_maturity
                    if len(str(date.day)) < 2:
                        day = '0' + str(date.day)
                    else:
                        day = str(date.day)
                    if len(str(date.month)) < 2:
                        month = '0' + str(date.month)
                    else:
                        month = str(date.month)
                    date_payment = day + '/' + month + '/' + str(date.year + 543)
                if date_payment:
                    move_ids += date_payment + '|'
                else:
                    move_ids += '|'
                # move_ids += strToDate(move.date_maturity).strftime("%d/%m/%Y") + '|'
                move_ids += str(move.name) + '|'

                if move.wht_type:
                    wht_type = str(move.wht_tax.amount)[0]
                    # if move.wht_type == '1%':
                    #     wht_type = '1'
                    # elif move.wht_type == '2%':
                    #     wht_type = '2'
                    # elif move.wht_type == '3%':
                    #     wht_type = '3'
                    # elif move.wht_type == '5%':
                    #     wht_type = '5'

                move_ids += str(wht_type) + '|'
                move_ids += str(move.amount_before_tax) + '|'
                move_ids += str(move.credit) + '|'

                if inv_row != len(move_line_ids):
                    move_ids += '1' + "\n"
                else:
                    move_ids += '1'

                # worksheet.write(inv_row, 0, move_ids, for_left)
                final_text = final_text_body + str(move_ids)

                inv_row += 1

        # ------------------------------------ End PND 53 -------------------------------------------------

        else:
            raise UserError(_('There is record this date range.'))

        print ('FINAL')
        print (final_text)

        values = {
            'name': "Witholding Report.txt",
            'res_model': 'ir.ui.view',
            'res_id': False,
            'type': 'binary',
            'public': True,
            'datas': base64.b64encode((final_text).encode("utf-8")),
        }
        attachment_id = self.env['ir.attachment'].sudo().create(values)
        download_url = '/web/content/' + str(attachment_id.id) + '?download=True'
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        # '/web/content/' + attachment.id + '?download=true'

        return {
            "type": "ir.actions.act_url",
            "url": str(base_url) + str(download_url),
            "target": "new",
        }
