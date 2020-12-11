# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today  itaas.co.th

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero, float_compare
import odoo.addons.decimal_precision as dp

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}
# Since invoice amounts are unsigned, this is how we know if money comes in or goes out
MAP_INVOICE_TYPE_PAYMENT_SIGN = {
    'out_invoice': 1,
    'in_refund': 1,
    'in_invoice': -1,
    'out_refund': -1,
}


class account_payment(models.Model):
    _inherit = "account.payment"

    payment_option = fields.Selection(
        [('full', 'Full Payment without Deduction'), ('partial', 'Full Payment with Deduction')],
        default='full', required=True, string='Payment Option')

    post_diff_acc = fields.Selection([('single', 'Single Account'), ('multi', 'Multiple Accounts')], default='single',
                                     string='Post Difference In To')
    writeoff_multi_acc_ids = fields.One2many('writeoff.accounts', 'payment_id', string='Write Off Accounts')

    ###########REMOVE ########################################
    purchase_or_sale = fields.Selection([('purchase', 'Purchase'), ('sale', 'Sale')])
    payment_cut_off_amount = fields.Float(string='Cut Off Payment Amount', digits=dp.get_precision('Account'),
                                          readonly=True, compute="get_payment_cut_off_amount")
    current_account_id = fields.Many2one('account.account', string='Current Account', compute='get_current_account_id')
    is_change_account = fields.Boolean(string='Change Account')
    payment_account_id = fields.Many2one('account.account', string='New Account')
    ###########--------#######################################
    amount_untaxed = fields.Monetary(string='Full Amount')
    require_write_off = fields.Boolean(string='Require write off account')
    remark = fields.Char(string='Payment Remark')
    ###########REMOVE ########################################
    wht = fields.Boolean(string="WHT")
    ################## About Cheque###############
    bank_cheque = fields.Boolean(string='Is Cheque', related='journal_id.bank_cheque')
    cheque_bank = fields.Many2one('res.bank', string="Bank")
    cheque_branch = fields.Char(string="Branch")
    cheque_number = fields.Char(string="Cheque Number")
    cheque_date = fields.Date(string="Cheque Date")
    cheque_reg_id = fields.Many2one('account.cheque.statement', string='Cheque Record')
    ################## About Cheque###############

    @api.depends('journal_id')
    def get_current_account_id(self):
        if self.payment_type in ('outbound',
                              'transfer') and self.journal_id.default_debit_account_id.id:
            self.current_account_id = self.journal_id.default_debit_account_id.id
        else:
            self.current_account_id = self.journal_id.default_credit_account_id.id

    @api.onchange('payment_difference')
    def check_require_write_off_account(self):
        amount = 0
        if self.writeoff_multi_acc_ids:
            for payment in self.writeoff_multi_acc_ids:
                amount += payment.amount
        precision = self.env['decimal.precision'].precision_get('Product Price')
        print ('-------DIFF--')
        print(self.payment_difference)
        print(amount)
        if float_compare(float(abs(self.payment_difference)), float(abs(amount)), precision_digits=precision) != 0:
            print ('REQUIRE=TRUE')
            self.require_write_off = True
        else:
            print('REQUIRE=FALSE')
            self.require_write_off = False


    @api.onchange('payment_option')
    def onchange_payment_option(self):
        if self.payment_option == 'full':
            self.payment_difference_handling = 'open'
            self.post_diff_acc = 'single'
        else:
            self.payment_difference_handling = 'reconcile'
            self.post_diff_acc = 'multi'

        if self.invoice_ids[0].type in ['in_invoice', 'out_refund']:
            self.purchase_or_sale = 'purchase'
        else:
            self.purchase_or_sale = 'sale'

    #when add write off then new pay amount will be calculated by deduct from diff amount
    @api.onchange('writeoff_multi_acc_ids')
    # @api.multi
    def onchange_writeoff_multi_accounts(self):
        if self.writeoff_multi_acc_ids:
            diff_amount = sum([line.amount for line in self.writeoff_multi_acc_ids])
            self.amount = self.invoice_ids and self.invoice_ids[0].amount_residual - diff_amount
            self.amount_untaxed = sum([invoice.amount_untaxed for invoice in self.invoice_ids])
            # print "onchange_writeoff_multi_accounts(self):"
            # print self.amount_untaxed



    def _get_move_vals(self, journal=None):
        """ Return dict to create the payment move
        """
        journal = journal or self.journal_id
        if not journal.sequence_id:
            raise UserError(_('Configuration Error !'), _('The journal %s does not have a sequence, please specify one.') % journal.name)
        if not journal.sequence_id.active:
            raise UserError(_('Configuration Error !'), _('The sequence of journal %s is deactivated.') % journal.name)

        if self.move_name:
            name = self.move_name
        else:
            name = journal.with_context(ir_sequence_date=self.payment_date).sequence_id.next_by_id()

        wht_personal_company = False
        if self.writeoff_multi_acc_ids:
            for woff_payment in self.writeoff_multi_acc_ids:
                if woff_payment.writeoff_account_id.wht and woff_payment.amt_percent and self.payment_type == 'outbound':
                    wht_personal_company = woff_payment.wht_personal_company


        return {
            'name': name,
            'date': self.payment_date,
            'ref': self.communication or '',
            'remark': self.remark,
            'cheque_bank': self.cheque_bank.id,
            'cheque_branch': self.cheque_branch,
            'cheque_number': self.cheque_number,
            'cheque_date': self.cheque_date,
            'company_id': self.company_id.id,
            'journal_id': journal.id,
            'wht_personal_company' : wht_personal_company,
        }

    #############call from account.payment post()############
    def _prepare_payment_moves(self):
        res = super(account_payment, self)._prepare_payment_moves()
        print('--RES BEFORE--')
        print(res)
        for payment in self:
            line_ids_new = []
            company_currency = payment.company_id.currency_id
            if payment.payment_difference_handling == 'reconcile' and payment.writeoff_multi_acc_ids:
                for line in (res[0]['line_ids']):
                    ###########Remove odoo standard write off as detection from write off account id, this will be ignore due to they use multi write off instead##
                    ##########JA - 22/07/2020 ########
                    if (line[2]['account_id']):
                        line_ids_new.append(line)

                for write_off_line in payment.writeoff_multi_acc_ids:
                    if payment.currency_id == company_currency:
                        write_off_balance = 0.0
                        currency_id = False
                    else:
                        write_off_balance = payment.currency_id._convert(write_off_line.amount, company_currency,
                                                                         payment.company_id, payment.payment_date)
                        currency_id = payment.currency_id.id

                    if payment.partner_type == 'customer':
                        line_ids_new.append((0, 0, {
                            'name': write_off_line.name,
                            'amount_currency': write_off_balance,
                            'currency_id': currency_id,
                            'debit': -write_off_line.amount < 0.0 and write_off_line.amount or 0.0,
                            'credit': -write_off_line.amount > 0.0 and -write_off_line.amount or 0.0,
                            'date_maturity': payment.payment_date,
                            'partner_id': payment.partner_id.commercial_partner_id.id,
                            'account_id': write_off_line.writeoff_account_id.id,
                            'payment_id': payment.id,
                            'wht_tax': write_off_line.deduct_item_id.id or False,
                            'wht_type': write_off_line.wht_type.id or False,
                            'amount_before_tax': write_off_line.amount_untaxed or 0.00,
                        }))
                    else:
                        line_ids_new.append((0, 0, {
                            'name': write_off_line.name,
                            'amount_currency': write_off_balance,
                            'currency_id': currency_id,
                            'debit': -write_off_line.amount > 0.0 and -write_off_line.amount or 0.0,
                            'credit': -write_off_line.amount < 0.0 and write_off_line.amount or 0.0,
                            'date_maturity': payment.payment_date,
                            'partner_id': payment.partner_id.commercial_partner_id.id,
                            'account_id': write_off_line.writeoff_account_id.id,
                            'payment_id': payment.id,
                            'wht_tax': write_off_line.deduct_item_id.id or False,
                            'wht_type': write_off_line.wht_type.id or False,
                            'amount_before_tax': write_off_line.amount_untaxed or 0.00,
                        }))

                res[0]['line_ids'] = line_ids_new
            res[0]['narration'] = payment.remark
        return res


    ############# Add payment cancel condition to cheque - by JA 08/10/2020 ##############

    def cancel(self):
        print
        "NEW Cancel"
        for rec in self:
            ############ This is for multiple check in one payment
            if rec.cheque_reg_id:
                # print ('--CHECK FOR ONE PAYMENT')
                ############ JA - 03/07/2020 #############
                if rec.cheque_reg_id.state != 'confirm':
                    rec.cheque_reg_id.sudo().action_cancel()
                    rec.cheque_reg_id.sudo().unlink()
                else:
                    raise UserError(_('เช็คได้ผ่านแล้ว กรุณาตรวจสอบก่อนยกเลิก'))
                ############ JA - 03/07/2020 #############


            ########## record wht reference number before cancel ###########
            ######### 22/06/2020 ###########################################
            for move_line in rec.move_line_ids:
                if move_line.wht_reference:
                    write_off_line = rec.writeoff_multi_acc_ids.filtered(
                        lambda x: x.wht_personal_company == move_line.wht_personal_company and not float_compare(
                            x.amount, move_line.credit, 2))
                    # print write_off_line
                    if write_off_line:
                        write_off_line.wht_reference = move_line.wht_reference
            ######### 22/06/2020 ###########################################

            super(account_payment, self).cancel()

    #############call from account.payment post()############
    # def _create_payment_entry(self, amount):
    #     """ Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
    #         Return the journal entry.
    #     """
    #     #print "_create_payment_entry"
    #     #print amount
    #     aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
    #     invoice_currency = False
    #     if self.invoice_ids and all([x.currency_id == self.invoice_ids[0].currency_id for x in self.invoice_ids]):
    #         # if all the invoices selected share the same currency, record the paiement in that currency too
    #         invoice_currency = self.invoice_ids[0].currency_id
    #
    #
    #     debit, credit, amount_currency, currency_id = aml_obj.with_context(
    #         date=self.payment_date)._compute_amount_fields(amount, self.currency_id, self.company_id.currency_id)
    #
    #     move = self.env['account.move'].create(self._get_move_vals())
    #     #print "MOVE LINE"
    #     #print len(move)
    #     # print move.name
    #
    #     # Write line corresponding to invoice payment
    #     counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
    #     counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
    #     #print "PART 1"
    #     #print counterpart_aml_dict
    #     counterpart_aml_dict.update({'currency_id': currency_id})
    #     counterpart_aml = aml_obj.create(counterpart_aml_dict)
    #     #print "MOVE LINE"
    #     #print len(move)
    #     precision = self.env['decimal.precision'].precision_get('Product Price')
    #
    #     # Reconcile with the invoices
    #     if self.payment_difference_handling == 'reconcile' and self.payment_difference:
    #         # print "with deduction"
    #         if self.post_diff_acc == 'single':
    #             #print "RECONCILE, DIFF and Single"
    #             writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
    #             debit_wo, credit_wo, amount_currency_wo, currency_id = aml_obj.with_context(
    #                 date=self.payment_date)._compute_amount_fields(self.payment_difference, self.currency_id,
    #                                                               self.company_id.currency_id)
    #             writeoff_line['name'] = _('Counterpart')
    #             writeoff_line['account_id'] = self.writeoff_account_id.id
    #             writeoff_line['debit'] = debit_wo
    #             writeoff_line['credit'] = credit_wo
    #             writeoff_line['amount_currency'] = amount_currency_wo
    #             writeoff_line['currency_id'] = currency_id
    #             writeoff_line['payment_id'] = self.id
    #             #print '9999999'
    #             aml_obj.create(writeoff_line)
    #             if counterpart_aml['debit']:
    #                 counterpart_aml['debit'] += credit_wo - debit_wo
    #             if counterpart_aml['credit']:
    #                 counterpart_aml['credit'] += debit_wo - credit_wo
    #             counterpart_aml['amount_currency'] -= amount_currency_wo
    #         if self.post_diff_acc == 'multi':
    #             #print "RECONCILE, DIFF and MULTI"
    #             write_off_total_amount = 0
    #             for woff_payment in self.writeoff_multi_acc_ids:
    #                 if self.payment_type == 'inbound':
    #                     woff_amount = woff_payment.amount
    #                 else:
    #                     woff_amount = - woff_payment.amount
    #
    #                 write_off_total_amount = woff_payment.amount
    #                 writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
    #                 debit_wo, credit_wo, amount_currency_wo, currency_id = aml_obj.with_context(
    #                     date=self.payment_date)._compute_amount_fields(woff_amount, self.currency_id,self.company_id.currency_id)
    #                 # if not self.currency_id != self.company_id.currency_id:
    #                 #     amount_currency_wo = 0
    #                 writeoff_line['name'] = woff_payment.name
    #                 writeoff_line['account_id'] = woff_payment.writeoff_account_id.id
    #                 writeoff_line['debit'] = debit_wo
    #                 writeoff_line['credit'] = credit_wo
    #                 writeoff_line['amount_currency'] = amount_currency_wo
    #                 writeoff_line['currency_id'] = woff_payment.currency_id.id
    #                 writeoff_line['payment_id'] = self.id
    #                 # writeoff_line['department_id'] = woff_payment.department_id.id
    #
    #                 if woff_payment.currency_id != self.currency_id:
    #                     raise UserError(_('Deduction currency must be the same with payment currency'))
    #
    #                 ###########amount before tax will allway in company currency
    #                 if self.currency_id != self.company_id.currency_id:
    #                     currency_id = self.currency_id.with_context(date=self.payment_date)
    #                     amount_before_tax = currency_id.compute(woff_payment.amount_untaxed, self.company_id.currency_id)
    #                 else:
    #                     amount_before_tax = woff_payment.amount_untaxed
    #
    #                 writeoff_line['amount_before_tax'] = amount_before_tax
    #                 ###############################################################
    #
    #                 if woff_payment.writeoff_account_id.wht and woff_payment.amt_percent and self.payment_type == 'outbound':
    #                     if woff_payment.amt_percent == 1:
    #                         writeoff_line['wht_type'] = '1%'
    #                     if woff_payment.amt_percent == 2:
    #                         writeoff_line['wht_type'] = '2%'
    #                     if woff_payment.amt_percent == 3:
    #                         writeoff_line['wht_type'] = '3%'
    #                     if woff_payment.amt_percent == 5:
    #                         writeoff_line['wht_type'] = '5%'
    #
    #                     # print "record to journal wht personal company"
    #                     # print woff_payment.wht_personal_company
    #                     # writeoff_line['wht_personal_company'] = 'personal'
    #
    #                 #print "Write off"
    #                 #print "PART 2"
    #                 #print writeoff_line
    #                 aml_obj.create(writeoff_line)
    #                 #print "MOVE LINE"
    #                 #print len(move)
    #                 # print "writeoff_line after"
    #                 # print writeoff_line
    #
    #                 #############to update all counter part to total payment
    #                 if counterpart_aml['debit'] or (counterpart_aml['debit'] == 0.0 and self.payment_type == 'outbound'):
    #                     counterpart_aml['debit'] += credit_wo - debit_wo
    #                 if counterpart_aml['credit'] or (counterpart_aml['credit'] == 0.0 and self.payment_type == 'inbound'):
    #                     counterpart_aml['credit'] += debit_wo - credit_wo
    #                 counterpart_aml['amount_currency'] -= amount_currency_wo
    #
    #             if self.writeoff_account_id and float_compare(float(self.payment_difference), float(write_off_total_amount),
    #                                                             precision_digits=precision) != 0:
    #
    #                 amount_final_diff = self.payment_difference - write_off_total_amount
    #
    #                 if self.payment_type != 'inbound':
    #                     amount_final_diff = (-1)*amount_final_diff
    #
    #                 writeoff_final_diff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
    #                 debit_wo, credit_wo, amount_currency_wo, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amount_final_diff, self.currency_id,
    #                                                               self.company_id.currency_id)
    #                 writeoff_final_diff_line['name'] = self.writeoff_account_id.name
    #                 writeoff_final_diff_line['account_id'] = self.writeoff_account_id.id
    #                 writeoff_final_diff_line['debit'] = debit_wo
    #                 writeoff_final_diff_line['credit'] = credit_wo
    #                 writeoff_final_diff_line['amount_currency'] = amount_currency_wo
    #                 writeoff_final_diff_line['currency_id'] = currency_id
    #                 writeoff_final_diff_line['payment_id'] = self.id
    #
    #                 #print "Final Diff"
    #                 #print "PART 3"
    #                 #print writeoff_final_diff_line
    #                 aml_obj.create(writeoff_final_diff_line)
    #                 #print "MOVE LINE"
    #                 #print len(move)
    #                 if counterpart_aml['debit']:
    #                     counterpart_aml['debit'] += credit_wo - debit_wo
    #                 if counterpart_aml['credit']:
    #                     counterpart_aml['credit'] += debit_wo - credit_wo
    #                 counterpart_aml['amount_currency'] -= amount_currency_wo
    #
    #     # Reconcile with the invoices
    #     if self.payment_difference_handling == 'open' and self.payment_difference:
    #         #print "OPEN and DIFF"
    #         if self.post_diff_acc == 'multi':
    #             #print "OPEN and DIFF and MULTI"
    #             for woff_payment in self.writeoff_multi_acc_ids:
    #                 if self.payment_type == 'inbound':
    #                     woff_amount = woff_payment.amount
    #                 else:
    #                     woff_amount = - woff_payment.amount
    #
    #                 writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
    #                 debit_wo, credit_wo, amount_currency_wo, currency_id = aml_obj.with_context(
    #                     date=self.payment_date)._compute_amount_fields(woff_amount, self.currency_id,
    #                                                                   self.company_id.currency_id)
    #                 # if not self.currency_id != self.company_id.currency_id:
    #                 #     amount_currency_wo = 0
    #                 writeoff_line['name'] = woff_payment.name
    #                 writeoff_line['account_id'] = woff_payment.writeoff_account_id.id
    #                 writeoff_line['debit'] = debit_wo
    #                 writeoff_line['credit'] = credit_wo
    #                 writeoff_line['amount_currency'] = amount_currency_wo
    #                 writeoff_line['currency_id'] = currency_id
    #                 writeoff_line['payment_id'] = self.id
    #                 writeoff_line['amount_before_tax'] = woff_payment.amount_untaxed
    #
    #                 if woff_payment.writeoff_account_id.wht and woff_payment.amt_percent and self.payment_type == 'outbound':
    #                     if woff_payment.amt_percent == 1:
    #                         writeoff_line['wht_type'] = '1%'
    #                     if woff_payment.amt_percent == 2:
    #                         writeoff_line['wht_type'] = '2%'
    #                     if woff_payment.amt_percent == 3:
    #                         writeoff_line['wht_type'] = '3%'
    #                     if woff_payment.amt_percent == 5:
    #                         writeoff_line['wht_type'] = '5%'
    #
    #                         # print "record to journal wht personal company"
    #                         # print woff_payment.wht_personal_company
    #                         # writeoff_line['wht_personal_company'] = 'personal'
    #
    #                 aml_obj.create(writeoff_line)
    #
    #                 if counterpart_aml['debit'] or (
    #                                 counterpart_aml['debit'] == 0.0 and self.payment_type == 'outbound'):
    #                     counterpart_aml['debit'] += credit_wo - debit_wo
    #                 if counterpart_aml['credit'] or (
    #                                 counterpart_aml['credit'] == 0.0 and self.payment_type == 'inbound'):
    #                     counterpart_aml['credit'] += debit_wo - credit_wo
    #
    #                 counterpart_aml['amount_currency'] -= amount_currency_wo
    #
    #     ##############if no invoice ################## Add 26/06/2019
    #     if not self.invoice_ids and self.writeoff_multi_acc_ids:
    #         print ("no invoice")
    #         write_off_total_amount = 0
    #         for woff_payment in self.writeoff_multi_acc_ids:
    #             if self.payment_type == 'inbound':
    #                 woff_amount = woff_payment.amount
    #             else:
    #                 woff_amount = - woff_payment.amount
    #
    #             write_off_total_amount = woff_payment.amount
    #             writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
    #             debit_wo, credit_wo, amount_currency_wo, currency_id = aml_obj.with_context(
    #                 date=self.payment_date)._compute_amount_fields(woff_amount, self.currency_id,
    #                                                                   self.company_id.currency_id)
    #             # if not self.currency_id != self.company_id.currency_id:
    #             #     amount_currency_wo = 0
    #             writeoff_line['name'] = woff_payment.name
    #             writeoff_line['account_id'] = woff_payment.writeoff_account_id.id
    #             writeoff_line['debit'] = debit_wo
    #             writeoff_line['credit'] = credit_wo
    #             writeoff_line['amount_currency'] = amount_currency_wo
    #             writeoff_line['currency_id'] = woff_payment.currency_id.id
    #             writeoff_line['payment_id'] = self.id
    #
    #
    #             if woff_payment.currency_id != self.currency_id:
    #                 raise UserError(_('Deduction currency must be the same with payment currency'))
    #
    #             ###########amount before tax will allway in company currency
    #             if self.currency_id != self.company_id.currency_id:
    #                 currency_id = self.currency_id.with_context(date=self.payment_date)
    #                 amount_before_tax = currency_id.compute(woff_payment.amount_untaxed,
    #                                                         self.company_id.currency_id)
    #             else:
    #                 amount_before_tax = woff_payment.amount_untaxed
    #
    #             writeoff_line['amount_before_tax'] = amount_before_tax
    #             ###############################################################
    #
    #             if woff_payment.writeoff_account_id.wht and woff_payment.amt_percent and self.payment_type == 'outbound':
    #                 if woff_payment.amt_percent == 1:
    #                     writeoff_line['wht_type'] = '1%'
    #                 if woff_payment.amt_percent == 2:
    #                     writeoff_line['wht_type'] = '2%'
    #                 if woff_payment.amt_percent == 3:
    #                     writeoff_line['wht_type'] = '3%'
    #                 if woff_payment.amt_percent == 5:
    #                     writeoff_line['wht_type'] = '5%'
    #
    #                 writeoff_line['wht_personal_company'] = woff_payment.wht_personal_company
    #
    #
    #             aml_obj.create(writeoff_line)
    #
    #             #############to update all counter part to total payment
    #             if counterpart_aml['debit'] or (
    #                             counterpart_aml['debit'] == 0.0 and self.payment_type == 'outbound'):
    #
    #                 counterpart_aml['debit'] += credit_wo - debit_wo
    #
    #                 print ("11111111")
    #
    #             if counterpart_aml['credit'] or (
    #                             counterpart_aml['credit'] == 0.0 and self.payment_type == 'inbound'):
    #                 counterpart_aml['credit'] += debit_wo - credit_wo
    #
    #                 print("22222222")
    #
    #             counterpart_aml['amount_currency'] -= amount_currency_wo
    #
    #         if self.writeoff_account_id and float_compare(float(self.payment_difference),
    #                                                       float(write_off_total_amount),
    #                                                       precision_digits=precision) != 0:
    #
    #             amount_final_diff = self.payment_difference - write_off_total_amount
    #
    #             if self.payment_type != 'inbound':
    #                 amount_final_diff = (-1) * amount_final_diff
    #
    #             writeoff_final_diff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
    #             debit_wo, credit_wo, amount_currency_wo, currency_id = aml_obj.with_context(
    #                 date=self.payment_date).compute_amount_fields(amount_final_diff, self.currency_id,
    #                                                               self.company_id.currency_id,
    #                                                               invoice_currency)
    #             writeoff_final_diff_line['name'] = self.writeoff_account_id.name
    #             writeoff_final_diff_line['account_id'] = self.writeoff_account_id.id
    #             writeoff_final_diff_line['debit'] = debit_wo
    #             writeoff_final_diff_line['credit'] = credit_wo
    #             writeoff_final_diff_line['amount_currency'] = amount_currency_wo
    #             writeoff_final_diff_line['currency_id'] = currency_id
    #             writeoff_final_diff_line['payment_id'] = self.id
    #
    #             if counterpart_aml['debit']:
    #                 counterpart_aml['debit'] += credit_wo - debit_wo
    #             if counterpart_aml['credit']:
    #                 counterpart_aml['credit'] += debit_wo - credit_wo
    #             counterpart_aml['amount_currency'] -= amount_currency_wo
    #
    #     ##############---start refer from standard #################
    #     if not self.currency_id.is_zero(self.amount):
    #         if not self.currency_id != self.company_id.currency_id:
    #             amount_currency = 0
    #         liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
    #         liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
    #
    #         ##########This is to add write off account id
    #         if self.payment_account_id:
    #             liquidity_aml_dict.update({'account_id': self.payment_account_id.id})
    #
    #         aml_obj.create(liquidity_aml_dict)
    #
    #
    #
    #     # validate the payment
    #     if not self.journal_id.post_at_bank_rec:
    #         move.post()
    #
    #     # reconcile the invoice receivable/payable line(s) with the payment
    #     if self.invoice_ids:
    #         self.invoice_ids.register_payment(counterpart_aml)
    #
    #     ##############----end refer from standard #################
    #
    #     return move

    # def get_wht_amount_pay_diff_amount(self):
    #     # print "get wht_amount diff"
    #     wht_amount = 0.0
    #     bank_fee_amount = 0.0
    #     little_amount = 0.0
    #     move_id = self.move_line_ids[0].move_id
    #     move_line_ids = self.env['account.move.line'].search([('move_id', '=', move_id.id)])
    #     #print move_line_ids
    #     if move_line_ids:
    #         #print "found move"
    #         for move_line in move_line_ids:
    #             #print move_line.name
    #             if move_line.account_id.wht:
    #                 wht_amount += move_line.debit
    #             if move_line.account_id.bank_fee:
    #                 bank_fee_amount += move_line.debit
    #             if move_line.account_id.diff_little_money:
    #                 little_amount += move_line.debit
    #
    #     return wht_amount
    #
    # def get_bank_fee_amount_pay_diff_amount(self):
    #     #print "get bank_fee_amount diff"
    #
    #     wht_amount = 0.0
    #     bank_fee_amount = 0.0
    #     little_amount = 0.0
    #     move_id = self.move_line_ids[0].move_id
    #     move_line_ids = self.env['account.move.line'].search([('move_id','=',move_id.id)])
    #     if move_line_ids:
    #         #print "found move"
    #         for move_line in move_line_ids:
    #             #print move_line.name
    #             if move_line.account_id.wht:
    #                 wht_amount += move_line.debit
    #             if move_line.account_id.bank_fee:
    #                 bank_fee_amount += move_line.debit
    #             if move_line.account_id.diff_little_money:
    #                 little_amount += move_line.debit
    #
    #
    #     return bank_fee_amount
    #
    # def get_little_amount_pay_diff_amount(self):
    #     #print "get little_amount diff"
    #
    #     wht_amount = 0.0
    #     bank_fee_amount = 0.0
    #     little_amount = 0.0
    #     move_id = self.move_line_ids[0].move_id
    #     move_line_ids = self.env['account.move.line'].search([('move_id', '=', move_id.id)])
    #     if move_line_ids:
    #         #print "found move"
    #         for move_line in move_line_ids:
    #             #print move_line.name
    #             if move_line.account_id.wht:
    #                 wht_amount += move_line.debit
    #             if move_line.account_id.bank_fee:
    #                 bank_fee_amount += move_line.debit
    #             if move_line.account_id.diff_little_money:
    #                 little_amount += move_line.debit
    #
    #     return little_amount

class writeoff_accounts(models.Model):
    _name = 'writeoff.accounts'

    deduct_item_id = fields.Many2one('account.tax', string='Deduction Item')
    writeoff_account_id = fields.Many2one('account.account', string="Difference Account",
                                          domain=[('deprecated', '=', False)], copy=False, required="1")
    wht = fields.Boolean(string="WHT", related='writeoff_account_id.wht', default=False)
    # wht_tax = fields.Many2one('account.tax', string="WHT", default=False)
    wht_type = fields.Many2one('account.wht.type', string='WHT Type', )
    name = fields.Char('Description')
    amount_untaxed = fields.Float(string='Full Amount')
    amt_percent = fields.Float(string='Amount(%)', digits=(16, 2))
    amount = fields.Float(string='Payment Amount', digits=(16, 2), required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)

    payment_id = fields.Many2one('account.payment', string='Payment Record')
    wht_reference = fields.Char(string='WHT Reference')

    # new for payment wizard only.
    # payment_wizard_id = fields.Many2one('account.register.payments', string='Payment Record')
    # payment_billing_id = fields.Many2one('register.billing.payments', string='Payment Record')
    # department_id = fields.Many2one('hr.department', string='Department')

    @api.onchange('writeoff_account_id')
    # @api.multi
    def _onchange_writeoff_account_id(self):
        if self.writeoff_account_id:
            self.name = self.writeoff_account_id.name

    @api.onchange('amt_percent','amount_untaxed')
    def _onchange_amt_percent(self):
        if self.amount_untaxed and self.amt_percent:
            self.amount = self.amount_untaxed * self.amt_percent / 100

    @api.onchange('deduct_item_id')
    # @api.multi
    def _onchange_deduct_item_id(self):
        # if self.payment_wizard_id:
        #     payment_vals = self.payment_wizard_id.get_payment_vals()
        #     self.amount_untaxed = payment_vals['amount_untaxed']
        #
        #     # new for payment billing only
        # if self.payment_billing_id:
        #     payment_vals = self.payment_billing_id.get_payment_vals()
        #     self.amount_untaxed = payment_vals['amount_untaxed']


        if self.deduct_item_id:
            tax_account_line_id = self.deduct_item_id.invoice_repartition_line_ids.filtered(lambda x: x.repartition_type == 'tax')
            if tax_account_line_id:
                account_id = tax_account_line_id.account_id.id
            else:
                account_id = False
            self.writeoff_account_id = account_id
            self.amt_percent = self.deduct_item_id.amount
            self.name = self.deduct_item_id.name
            self.wht_type = self.deduct_item_id.wht_type
            if not self.amount_untaxed:
                self.amount_untaxed = self.payment_id.invoice_ids[0].amount_untaxed
            self.amount = self.amount_untaxed * self.deduct_item_id.amount / 100


