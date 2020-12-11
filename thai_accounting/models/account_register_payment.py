# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today  itaas.co.th

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero, float_compare
import odoo.addons.decimal_precision as dp
from itertools import groupby

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


class account_register_payments(models.Model):
    _name = "account.register.payments"
    _inherit = 'account.abstract.payment'


    multi = fields.Boolean(string='Multi',
                           help='Technical field indicating if the user selected invoices from multiple partners or from different types.')

    payment_option = fields.Selection(
        [('full', 'Full Payment without Deduction'), ('partial', 'Full Payment with Deduction')],
        default='full', required=True, string='Payment Option')
    post_diff_acc = fields.Selection([('single', 'Single Account'), ('multi', 'Multiple Accounts')], default='single',
                                     string='Post Difference In To')
    writeoff_multi_acc_ids = fields.One2many('writeoff.accounts', 'payment_wizard_id', string='Write Off Accounts')
    # wht = fields.Boolean(string="WHT")
    payment_difference_handling = fields.Selection([('open', 'Keep open'), ('reconcile', 'Mark invoice as fully paid')],
                                                   default='open', string="Payment Difference", copy=False)
    payment_difference = fields.Monetary(compute='_compute_payment_difference', readonly=True)
    writeoff_account_id = fields.Many2one('account.account', string="Difference Account",
                                          domain=[('deprecated', '=', False)], copy=False)
    invoice_ids = fields.Many2many('account.invoice', 'account_invoice_payment_wizard_rel', 'payment_wizard_id',
                                   'invoice_id',
                                   string="Invoices", copy=False, readonly=True)
    purchase_or_sale = fields.Selection([('purchase', 'Purchase'), ('sale', 'Sale')])
    # invoice_line_tax_id = fields.Many2one('account.tax')
    # tax_id = fields.Char(string='Tax ID')
    amount_untaxed = fields.Monetary(string='Payment Untax Amount')
    remark = fields.Char(string="Payment Remark")
    # this is the old bank text input
    # cheque_bank = fields.Char(string="Bank")
    bank_cheque = fields.Boolean(string='Is Cheque', related='journal_id.bank_cheque')
    # this is new bank list from res.bank
    cheque_bank = fields.Many2one('res.bank', string="Bank")
    cheque_branch = fields.Char(string="Branch")
    cheque_number = fields.Char(string="Cheque Number")
    cheque_date = fields.Date(string="Cheque Date")
    require_write_off_account = fields.Boolean(string='Require write off account')
    current_account_id = fields.Many2one('account.account', string='Current Account', compute='get_current_account_id')
    is_change_account = fields.Boolean(string='Change Account')
    payment_account_id = fields.Many2one('account.account', string='New Account')

    group_invoices = fields.Boolean(string="Group Invoices", help="""If enabled, groups invoices by commercial partner, invoice account,
                                                                        type and recipient bank account in the generated payments. If disabled,
                                                                        a distinct payment will be generated for each invoice.""")
    show_communication_field = fields.Boolean(compute='_compute_show_communication_field')

    @api.depends('invoice_ids.partner_id', 'group_invoices')
    def _compute_show_communication_field(self):
        """ We allow choosing a common communication for payments if the group
        option has been activated, and all the invoices relate to the same
        partner.
        """
        for record in self:
            record.show_communication_field = len(record.invoice_ids) == 1 \
                                              or record.group_invoices and len(
                record.mapped('invoice_ids.partner_id.commercial_partner_id')) == 1

    @api.onchange('journal_id')
    def _onchange_journal(self):
        res = super(account_register_payments, self)._onchange_journal()
        active_ids = self._context.get('active_ids')
        invoices = self.env['account.invoice'].browse(active_ids)
        self.amount = abs(self._compute_payment_amount(invoices))
        return res

    @api.model
    def default_get(self, fields):
        rec = super(account_register_payments, self).default_get(fields)
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')


        # Checks on context parameters
        if not active_model or not active_ids:
            raise UserError(
                _("Programmation error: wizard action executed without active_model or active_ids in context."))
        if active_model != 'account.invoice':
            raise UserError(_(
                "Programmation error: the expected model for this action is 'account.invoice'. The provided one is '%d'.") % active_model)
        if not active_ids:
            raise UserError(_("Programming error: wizard action executed without active_ids in context."))

        # Checks on received invoice records
        invoices = self.env[active_model].browse(active_ids)

        if any(invoice.state != 'open' for invoice in invoices):
            raise UserError(_("You can only register payments for open invoices"))

        if any(inv.currency_id != invoices[0].currency_id for inv in invoices):
            raise UserError(_("In order to pay multiple invoices at once, they must use the same currency."))

        #########this is V10- function pay only one partner #########################################
        # if any(inv.commercial_partner_id != invoices[0].commercial_partner_id for inv in invoices):
        #     raise UserError(
        #         _("In order to pay multiple invoices at once, they must belong to the same commercial partner."))

        # if any(MAP_INVOICE_TYPE_PARTNER_TYPE[inv.type] != MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type] for inv in
        #        invoices):
        #     raise UserError(_("You cannot mix customer invoices and vendor bills in a single payment."))

        ##################### new function to paid multiple invoice with multiple partner#############
        # Look if we are mixin multiple commercial_partner or customer invoices with vendor bills
        multi = any(inv.commercial_partner_id != invoices[0].commercial_partner_id
                    or MAP_INVOICE_TYPE_PARTNER_TYPE[inv.type] != MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type]
                    for inv in invoices)

        total_amount = sum(inv.residual * MAP_INVOICE_TYPE_PAYMENT_SIGN[inv.type] for inv in invoices)
        total_untaxed = sum(inv.amount_untaxed for inv in invoices)

        if invoices[0].type in ['in_invoice', 'out_refund']:
            purchase_or_sale = 'purchase'
        else:
            purchase_or_sale = 'sale'

        rec.update({
            'amount': abs(total_amount),
            'currency_id': invoices[0].currency_id.id,
            'payment_type': total_amount > 0 and 'inbound' or 'outbound',
            'partner_id': False if multi else invoices[0].commercial_partner_id.id,
            'partner_type': False if multi else MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type],
            'communication': ' '.join([ref for ref in invoices.mapped('reference') if ref]),
            'amount_untaxed': abs(total_untaxed),
            'purchase_or_sale': purchase_or_sale,
            'multi': multi,
        })
        return rec





    #############Remove 18/03/2019
    # @api.model
    # def default_get(self, fields):
    #     rec = super(account_register_payments, self).default_get(fields)
    #     context = dict(self._context or {})
    #     #print "DEFAULT"
    #     #print context
    #     active_model = context.get('active_model')
    #     active_ids = context.get('active_ids')
    #
    #     # Checks on context parameters
    #     if not active_model or not active_ids:
    #         raise UserError(
    #             _("Programmation error: wizard action executed without active_model or active_ids in context."))
    #     if active_model != 'account.invoice':
    #         raise UserError(_(
    #             "Programmation error: the expected model for this action is 'account.invoice'. The provided one is '%d'.") % active_model)
    #
    #     # Checks on received invoice records
    #     invoices = self.env[active_model].browse(active_ids)
    #     #print "INVOICES"
    #     #print invoices
    #     # print "Default Get"
    #     # print invoice_ids
    #     if any(invoice.state != 'open' for invoice in invoices):
    #         raise UserError(_("You can only register payments for open invoices"))
    #
    #     if any(inv.currency_id != invoices[0].currency_id for inv in invoices):
    #         raise UserError(_("In order to pay multiple invoices at once, they must use the same currency."))
    #
    #     #########this is V10- function pay only one partner #########################################
    #     # if any(inv.commercial_partner_id != invoices[0].commercial_partner_id for inv in invoices):
    #     #     raise UserError(
    #     #         _("In order to pay multiple invoices at once, they must belong to the same commercial partner."))
    #
    #     # if any(MAP_INVOICE_TYPE_PARTNER_TYPE[inv.type] != MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type] for inv in
    #     #        invoices):
    #     #     raise UserError(_("You cannot mix customer invoices and vendor bills in a single payment."))
    #
    #     ##################### new function to paid multiple invoice with multiple partner#############
    #     # Look if we are mixin multiple commercial_partner or customer invoices with vendor bills
    #     multi = any(inv.commercial_partner_id != invoices[0].commercial_partner_id
    #                 or MAP_INVOICE_TYPE_PARTNER_TYPE[inv.type] != MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type]
    #                 for inv in invoices)
    #
    #     total_amount = sum(inv.residual * MAP_INVOICE_TYPE_PAYMENT_SIGN[inv.type] for inv in invoices)
    #     total_untaxed = sum(inv.amount_untaxed for inv in invoices)
    #
    #     if invoices[0].type in ['in_invoice', 'out_refund']:
    #         purchase_or_sale = 'purchase'
    #     else:
    #         purchase_or_sale = 'sale'
    #
    #     rec.update({
    #         'amount': abs(total_amount),
    #         'currency_id': invoices[0].currency_id.id,
    #         'payment_type': total_amount > 0 and 'inbound' or 'outbound',
    #         'partner_id': False if multi else invoices[0].commercial_partner_id.id,
    #         'partner_type': False if multi else MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type],
    #         'communication': ' '.join([ref for ref in invoices.mapped('reference') if ref]),
    #         'amount_untaxed': abs(total_untaxed),
    #         'purchase_or_sale': purchase_or_sale,
    #         'multi': multi,
    #     })
    #     return rec

    # @api.multi
    def _groupby_invoices(self):
        '''Groups the invoices linked to the wizard.

        If the group_invoices option is activated, invoices will be grouped
        according to their commercial partner, their account, their type and
        the account where the payment they expect should end up. Otherwise,
        invoices will be grouped so that each of them belongs to a
        distinct group.

        :return: a dictionary mapping, grouping invoices as a recordset under each of its keys.
        '''
        if not self.group_invoices:
            return {inv.id: inv for inv in self.invoice_ids}

        results = {}
        # Create a dict dispatching invoices according to their commercial_partner_id, account_id, invoice_type and partner_bank_id
        for inv in self.invoice_ids:
            partner_id = inv.commercial_partner_id.id
            account_id = inv.account_id.id
            invoice_type = MAP_INVOICE_TYPE_PARTNER_TYPE[inv.type]
            recipient_account = inv.partner_bank_id
            key = (partner_id, account_id, invoice_type, recipient_account)
            if not key in results:
                results[key] = self.env['account.invoice']
            results[key] += inv
        return results

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

        if float_compare(float(abs(self.payment_difference)), float(amount), precision_digits=precision) != 0:
            self.require_write_off_account = True
        else:
            self.require_write_off_account = False

    @api.onchange('payment_type')
    def _onchange_payment_type(self):
        if self.payment_type:
            return {'domain': {'payment_method_id': [('payment_type', '=', self.payment_type)]}}

    #############Remove and apply below function instead 18/03/2019 ######
    # @api.model
    # def _compute_payment_amount(self, invoice_ids):
    #     payment_currency = self.currency_id or self.journal_id.currency_id or self.journal_id.company_id.currency_id
    #
    #     total = 0
    #     for inv in invoice_ids:
    #         if inv.currency_id == payment_currency:
    #             total += MAP_INVOICE_TYPE_PAYMENT_SIGN[inv.type] * inv.residual_company_signed
    #         else:
    #             amount_residual = inv.company_currency_id.with_context(date=self.payment_date).compute(
    #                 inv.residual_company_signed, payment_currency)
    #             total += MAP_INVOICE_TYPE_PAYMENT_SIGN[inv.type] * amount_residual
    #
    #     return total

    #########Replace above function by this original function
    @api.multi
    def _compute_payment_amount(self, invoices=None, currency=None):
        '''Compute the total amount for the payment wizard.

        :param invoices: If not specified, pick all the invoices.
        :param currency: If not specified, search a default currency on wizard/journal.
        :return: The total amount to pay the invoices.
        '''

        # Get the payment invoices
        if not invoices:
            invoices = self.invoice_ids

        # Get the payment currency
        if not currency:
            currency = self.currency_id or self.journal_id.currency_id or self.journal_id.company_id.currency_id or invoices and \
                                                                                                                    invoices[
                                                                                                                        0].currency_id

        # Avoid currency rounding issues by summing the amounts according to the company_currency_id before
        total = 0.0
        groups = groupby(invoices, lambda i: i.currency_id)
        for payment_currency, payment_invoices in groups:
            amount_total = sum([MAP_INVOICE_TYPE_PAYMENT_SIGN[i.type] * i.residual_signed for i in payment_invoices])
            if payment_currency == currency:
                total += amount_total
            else:
                total += payment_currency._convert(amount_total, currency, self.env.user.company_id,
                                                   self.payment_date or fields.Date.today())
        return total

    @api.multi
    def _prepare_payment_vals(self, invoices):
        '''Create the payment values.

        :param invoices: The invoices that should have the same commercial partner and the same type.
        :return: The payment values as a dictionary.
        '''

        amount = self._compute_payment_amount(invoices=invoices) if self.multi else self.amount
        payment_type = ('inbound' if amount > 0 else 'outbound') if self.multi else self.payment_type
        bank_account = self.multi and invoices[0].partner_bank_id or self.partner_bank_account_id
        pmt_communication = self.show_communication_field and self.communication \
                            or self.group_invoices and ' '.join([inv.reference or inv.number for inv in invoices]) \
                            or invoices[
                                0].reference  # in this case, invoices contains only one element, since group_invoices is False


        ############## new for multi-write-off############
        writeoff_multi_ids = []
        for writeoff_multi in self.writeoff_multi_acc_ids:
            writeoff_multi_ids.append(writeoff_multi.id)

        return {
            'journal_id': self.journal_id.id,
            'payment_method_id': self.payment_method_id.id,
            'payment_date': self.payment_date,
            'communication': pmt_communication,
            'invoice_ids': [(6, 0, invoices.ids)],
            'payment_type': payment_type,
            'amount': abs(amount),
            'currency_id': self.currency_id.id,
            'partner_id': invoices[0].commercial_partner_id.id,
            'payment_account_id': self.payment_account_id.id,
            'partner_bank_account_id': bank_account.id,
            'partner_type': MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type],
            'multi': False,
            #################
            'post_diff_acc': self.post_diff_acc,
            'payment_difference_handling': self.payment_difference_handling,
            'payment_difference': self.payment_difference,
            'writeoff_multi_acc_ids': [(4, writeoff_multi.id, None) for writeoff_multi in
                                       self.writeoff_multi_acc_ids],
            'amount_untaxed': self.amount_untaxed,
            'remark': self.remark,
            'cheque_bank': self.cheque_bank.id,
            'cheque_branch': self.cheque_branch,
            'cheque_number': self.cheque_number,
            'cheque_date': self.cheque_date,
        }

    @api.multi
    def get_payments_vals(self):
        '''Compute the values for payments.

        :return: a list of payment values (dictionary).
        '''
        if self.multi:
            groups = self._groupby_invoices()
            return [self._prepare_payment_vals(invoices) for invoices in groups.values()]
        return [self._prepare_payment_vals(self.invoice_ids)]

    @api.multi
    def create_payments(self):
        '''Create payments according to the invoices.
        Having invoices with different commercial_partner_id or different type (Vendor bills with customer invoices)
        leads to multiple payments.
        In case of all the invoices are related to the same commercial_partner_id and have the same type,
        only one payment will be created.

        :return: The ir.actions.act_window to show created payments.
        '''
        Payment = self.env['account.payment']
        payments = Payment
        for payment_vals in self.get_payments_vals():
            payments += Payment.create(payment_vals)
        payments.post()

        action_vals = {
            'name': _('Payments'),
            'domain': [('id', 'in', payments.ids), ('state', '=', 'posted')],
            'view_type': 'form',
            'res_model': 'account.payment',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
        if len(payments) == 1:
            action_vals.update({'res_id': payments[0].id, 'view_mode': 'form'})
        else:
            action_vals['view_mode'] = 'tree,form'
        return action_vals


    def _get_invoices(self):
        context = dict(self._context or {})
        #print "CONTEXT"
        #print context
        active_model = context.get('active_model')
        #print "ACTIVE MODEL"
        #print active_model
        active_ids = context.get('active_ids')
        #print "ACTIVE IDS"
        #print active_ids
        invoice_ids = self.env[active_model].browse(active_ids)
        return invoice_ids

    def get_payment_vals(self):
        """ Hook for extension """
        # update and return write off in order to pay with account.payment
        writeoff_multi_ids = []
        for writeoff_multi in self.writeoff_multi_acc_ids:
            writeoff_multi_ids.append(writeoff_multi.id)

        return {
            'journal_id': self.journal_id.id,
            'payment_method_id': self.payment_method_id.id,
            'payment_date': self.payment_date,
            'communication': self.communication,
            'payment_type': self.payment_type,
            'amount': self.amount,
            'post_diff_acc': self.post_diff_acc,
            'payment_account_id': self.payment_account_id,
            'payment_difference_handling': self.payment_difference_handling,
            'payment_difference': self.payment_difference,
            'writeoff_multi_acc_ids': [(4, writeoff_multi.id, None) for writeoff_multi in
                                       self.writeoff_multi_acc_ids],
            'amount_untaxed': self.amount_untaxed,
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
            'partner_type': self.partner_type,
            'remark': self.remark,
            'cheque_bank': self.cheque_bank.id,
            'cheque_branch': self.cheque_branch,
            'cheque_number': self.cheque_number,
            'cheque_date': self.cheque_date,

        }

    # compute payment difference from total invoice and new pay amount for "register with wizard but" but single invoice use existing function

    @api.one
    @api.depends('amount', 'payment_date', 'currency_id')
    def _compute_payment_difference(self):
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_ids = context.get('active_ids')
        invoice_ids = self.env[active_model].browse(active_ids)
        total_invoice_amount = self._compute_payment_amount(invoice_ids)
        if len(invoice_ids) == 0:
            return
        if invoice_ids[0].type in ['in_invoice', 'out_refund']:
            # print ('supplier')
            # print (self.amount)
            # print (total_invoice_amount)
            # print (self.payment_difference)
            self.payment_difference = self.amount - abs(total_invoice_amount)
            # print (self.payment_difference)
        else:
            # print('customer')
            # print(total_invoice_amount)
            # print(self.amount)
            # print(self.payment_difference)
            self.payment_difference = total_invoice_amount - self.amount
            # print (self.payment_difference)

    @api.onchange('payment_option')
    def onchange_payment_option(self):
        if self.payment_option == 'full':
            self.payment_difference_handling = 'open'
            self.post_diff_acc = 'single'
        else:
            self.payment_difference_handling = 'reconcile'
            self.post_diff_acc = 'multi'

    # calculate writeoff amount
    @api.onchange('writeoff_multi_acc_ids')
    @api.multi
    def onchange_writeoff_multi_accounts(self):
        if self.writeoff_multi_acc_ids:
            diff_amount = sum([line.amount for line in self.writeoff_multi_acc_ids])
            # print "DIFF AMOUNT- AR"
            # print diff_amount

            context = dict(self._context or {})
            #print "CONTEXT"
            #print context
            active_model = context.get('active_model')
            #print "ACTIVE MODEL"
            #print active_model
            active_ids = context.get('active_ids')
            #print "ACTIVE IDS"
            #print active_ids
            invoice_ids = self.env[active_model].browse(active_ids)
            #print invoice_ids
            total_invoice_amount = self._compute_payment_amount(self._get_invoices())
            # print ("TOTAL INVOICE AR")
            # print (total_invoice_amount)
            self.amount = abs(total_invoice_amount) - diff_amount
