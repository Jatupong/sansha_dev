# -*- coding: utf-8 -*-
# Copyright (C) 2016-2017  Technaureus Info Solutions(<http://technaureus.com/>).

from datetime import datetime
from odoo import tools
# from odoo import api, fields, models, _
from odoo.tools.translate import _
from odoo import api, models, fields, _
import xlwt
import time
import xlsxwriter
import base64
from datetime import datetime, date
from odoo.exceptions import UserError
from odoo.tools import misc
import operator
import locale
from odoo.tools import float_compare, float_is_zero
from dateutil.relativedelta import relativedelta
import calendar

def strToDate(dt):
    return date(int(dt[0:4]), int(dt[5:7]), int(dt[8:10]))

class wizard_payment_report(models.TransientModel):
    _name = 'wizard.payment.report'

    partner_ids = fields.Many2many('res.partner', string='Partner')
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')
    total_supplier = fields.Integer(string='Total Supplier')
    from_no = fields.Integer(string='Start From',default=1)
    to_no = fields.Integer(string='End To')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)

    # @api.onchange('date_from','date_to')
    # def onchange_date_from_to(self):
    #
    #     purchase_ids = self.env['supplier.evaluation.line'].search([('date','>=',self.date_from),('date','<=',self.date_to)])
    #
    #     supplier_ids = []
    #     for purchase in purchase_ids:
    #         if purchase.partner_id not in supplier_ids:
    #             supplier_ids.append(purchase.partner_id)
    #
    #     self.total_supplier = len(supplier_ids)
    #     self.to_no = len(supplier_ids)
    #
    # @api.model
    # def default_get(self, fields):
    #     res = super(wizard_payment_report, self).default_get(fields)
    #     curr_date = datetime.now()
    #     from_date = datetime(curr_date.year, 1, 1).date() or False
    #     to_date = datetime(curr_date.year, curr_date.month, curr_date.day).date() or False
    #     res.update({'date_from': str(from_date), 'date_to': str(to_date)})
    #     return res
    #
    # def print_pdf_report(self, data):
    #     print ('print_pdf_report')
    #
    #     data = {}
    #     data['form'] = self.read(['date_from', 'date_to', 'partner_ids', 'company_id','from_no','to_no'])[0]
    #     # print (data)
    #     return self.env.ref('itaas_print_payment_report.report_supplier_evaluation').report_action(self, data=data,
    #                                                                                           config=False)


