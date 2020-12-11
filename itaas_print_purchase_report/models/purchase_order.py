# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from bahttext import bahttext
import math
from bahttext import bahttext
from num2words import num2words
import locale
from odoo.exceptions import UserError
from datetime import datetime, date

from odoo import api, fields, models, _
from datetime import datetime, date
import dateutil.parser
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero, float_compare
from datetime import datetime, timedelta

class purchase_order(models.Model):
    _inherit = "purchase.order"

    contact_person = fields.Many2one('res.partner', string="Contact Person")
    validate_uid = fields.Many2one('res.users', string="Authorized Person")
    validate_date = fields.Date(string="Validated Date")
    request_uid = fields.Many2one('res.users', string="Purchase Request")
    confirm_uid = fields.Many2one('res.users', 'Confirm')

    show_product_code_on_purchase = fields.Boolean(string='Show Code in Report')

    # @api.multi
    def action_rfq_send(self):
        '''
        This function opens a window to compose an email, with the edi purchase template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            if self.env.context.get('send_rfq', False):
                template_id = ir_model_data.get_object_reference('purchase', 'purchase.email_template_edi_purchase')[1]
            else:
                template_id = ir_model_data.get_object_reference('itaas_print_purchase_report',
                                                                 'new_email_template_edi_purchase_done')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'purchase.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': "purchase.mail_template_data_notification_email_purchase_order",
            'purchase_mark_rfq_sent': True,
            'force_email': True
        })
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def get_lines(self, data, max_line):
        # this function will count number of \n
        # print  data
        line_count = data.count("\n")
        # print (line_count)
        # print (max_line)
        if not line_count:
            # print ("line 0 - no new line or only one line")

            # lenght the same with line max
            if not len(data) % max_line:
                line_count = len(data) / max_line
            # lenght not the same with line max
            # if less than line max then will be 0 + 1
            # if more than one, example 2 line then will be 1 + 1
            else:
                # print (len(data))
                line_count = len(data) / max_line
                line_count = math.ceil(line_count)
                # roundup(line_count)
                # line_count = len(data) / max_line + 1
        elif line_count:
            # print ("line not 0 - has new line")
            # print line_count
            # if have line count mean has \n then will be add 1 due to the last row have not been count \n
            line_count += 1
            data_line_s = data.split('\n')
            for x in range(0, len(data_line_s), 1):
                # print data_line_s[x]
                if len(data_line_s[x]) > max_line:
                    # print "more than one line"
                    line_count += len(data_line_s[x]) / max_line
        # print("final line")
        # print(line_count)
        if line_count > 1:
            line_count = line_count * 0.8
        return line_count

    def get_break_line(self, max_body_height, new_line_height, row_line_height, max_line_lenght):
        break_page_line = []
        count_height = 0
        count = 1

        for line in self.order_line:
            line_name = self.get_lines(line.name, max_line_lenght)
            line_height = row_line_height * line_name
            # print (line_height)

            ##############
            count_height += line_height
            # print ('COUNT-H')
            # print (count_height)
            # print (max_body_height)
            if count_height > max_body_height:
                # print ('OVER H')
                break_page_line.append(count - 1)
                count_height = line_height
            count += 1
        # last page
        break_page_line.append(count - 1)
        return break_page_line

    def get_pr_id(self):
        pr_id = self.order_line.filtered(lambda x: x.pr_id)

        if pr_id:
            word = ""
            for line in pr_id:
                word = word + line.pr_id.name
            return word
        else:
            return False


    # @api.multi
    def button_confirm(self):
        res = super(purchase_order, self).button_confirm()
        for order in self:
            order.write({'request_uid': self.env.user.id})
            order.write({'confirm_uid': self.env.user.id})
        return res

    # @api.multi
    def button_approve(self):
        self.write({'state': 'purchase','validate_uid': self.env.user.id,'validate_date': date.today()})
        return super(purchase_order, self).button_approve()

    # @api.multi
    def button_draft(self):
        self.write({'state': 'draft','validate_uid': False,'validate_date': False})
        return {}

    def baht_text(self, amount_total):
        return bahttext(amount_total)

    def num2_words(self, amount_total):
        before_point = ""
        amount_total_str = str(amount_total)
        for i in range(0,len(amount_total_str)):
            if amount_total_str[i] != ".":
                before_point += amount_total_str[i]
            else:
                break

        after_point = float(amount_total) - float(before_point)
        after_point = locale.format("%.2f", float(after_point), grouping=True)
        after_point = float(after_point)
        before_point = float(before_point)

        # print before_point
        # print after_point
        before_point_str = num2words(before_point)
        after_point_str = num2words(after_point)
        if after_point_str == 'zero':
            before_point_str += ' Only'
        else:
            for i in range(4,len(after_point_str)):
                before_point_str += after_point_str[i]

        n2w_origianl = before_point_str
        #print n2w_origianl
        # n2w_origianl = num2words(float(amount_total))
        n2w_new = ""
        for i in range(len(n2w_origianl)):
            if i == 0:
                n2w_new += n2w_origianl[i].upper()
            else:
                if n2w_origianl[i] != ",":
                    if n2w_origianl[i - 1] == " ":
                        n2w_new += n2w_origianl[i].upper()
                    else:
                        n2w_new += n2w_origianl[i]

        # print n2w_origianl
        # print n2w_new
        return n2w_new


class purchase_order_line(models.Model):
    _inherit = "purchase.order.line"

    discount_amount = fields.Float('Discount (Amount)', default=0.0)
    department_id = fields.Many2one('hr.department', string='แผนก')

    # get total description line
    def get_line(self, data):
        return data.count("\n")

        # option discount amount per unit or price sub total

    @api.depends('product_qty', 'price_unit', 'discount', 'taxes_id', 'discount_amount')
    def _compute_amount(self):
        """
        Compute the amounts of the PO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            if line.discount_amount > 0.0:
                if self.env.user.company_id.discount_amount_condition and self.env.user.company_id.discount_amount_condition == 'unit':
                    price -= line.discount_amount
                else:
                    price -= line.discount_amount / line.product_qty

            taxes = line.taxes_id.compute_all(price, line.order_id.currency_id, line.product_qty,
                                              product=line.product_id, partner=line.order_id.partner_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    @api.onchange('product_id')
    def onchange_product_id(self):
        domain = super(purchase_order_line, self).onchange_product_id()
        if self.product_id:
            vals = {}
            vals['name'] = self.product_id.name
            self.update(vals)

        return domain






