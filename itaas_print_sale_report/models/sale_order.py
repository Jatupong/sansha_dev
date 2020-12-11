# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from bahttext import bahttext
from odoo.exceptions import UserError
from datetime import datetime, date
from bahttext import bahttext
from num2words import num2words
import locale

class SaleOrder_inherit(models.Model):
    _inherit ="sale.order"

    discount_type = fields.Selection([('Fixed', 'Fixed'), ('Percentage', 'Percentage')], string='Discount Method',
                                     states={'draft': [('readonly', False)]})
    confirm_uid = fields.Many2one('res.users', 'Confirm')
    discounted_amount = fields.Float(compute='disc_amount', string='Discounted Amount', readonly=True)

    discount_view = fields.Selection([('After Tax', 'After Tax'), ('Before Tax', 'Before Tax')], string='Discount Type',
                                     states={'draft': [('readonly', False)]},
                                     help='Choose If After or Before applying Taxes type of the Discount')
    discount_value = fields.Float(string='Discount Value', states={'draft': [('readonly', False)]},
                                  help='Choose the value of the Discount')

    show_product_code_on_sale = fields.Boolean(string='Show Code in Quote')

    def get_lines(self, data, max_line):
        # this function will count number of \n
        # print  data
        line_count = data.count("\n")
        if not line_count:
            #  print "line 0 - no new line or only one line"
            # lenght the same with line max
            if not len(data) % max_line:
                line_count = len(data) / max_line
            # lenght not the same with line max
            # if less than line max then will be 0 + 1
            # if more than one, example 2 line then will be 1 + 1
            else:
                line_count = len(data) / max_line + 1
        elif line_count:
            # print "line not 0 - has new line"
            # print line_count
            # if have line count mean has \n then will be add 1 due to the last row have not been count \n
            line_count += 1
            data_line_s = data.split('\n')
            for x in range(0, len(data_line_s), 1):
                # print data_line_s[x]
                if len(data_line_s[x]) > max_line:
                    # print "more than one line"
                    line_count += len(data_line_s[x]) / max_line
        if line_count > 1:
            ##############if more then one line, it is new line not new row, so hight will be 80%
            line_count = line_count * 0.8
        return line_count

    def get_break_line(self, max_body_height, new_line_height, row_line_height, max_line_lenght):
        break_page_line = []
        count_height = 0
        count = 1

        for line in self.order_line:
            line_name = self.get_lines(line.name, max_line_lenght)
            # remove by row height to line
            # line_height = row_line_height + ((self.get_line(line.name, max_line_lenght)) * new_line_height)
            line_height = row_line_height * line_name
            count_height += line_height
            if count_height > max_body_height:
                break_page_line.append(count - 1)
                count_height = line_height
            count += 1
        # last page
        break_page_line.append(count - 1)

        return break_page_line

    def action_confirm(self):
        self.confirm_uid = self.env.uid
        return super(SaleOrder_inherit, self).action_confirm()

    def action_validate(self):
        self.validate_uid = self.env.uid
        return super(SaleOrder_inherit, self).action_validate()

    # @api.multi
    def print_quotation(self):
        self.filtered(lambda s: s.state == 'draft').write({'state': 'sent'})
        return self.env.ref('itaas_print_sale_report.quotations_report').report_action(self)

    # @api.multi
    def action_quotation_send(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('itaas_print_sale_report', 'new_email_template_edi_sale')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'sale.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "sale.mail_template_data_notification_email_sale_order",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

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

    # @api.multi
    # def _prepare_invoice(self):
    #     res = super(SaleOrder_inherit, self)._prepare_invoice()
    #     if self.discount_view and self.discount_type and self.discount_value:
    #         res['discount_view'] = self.discount_view
    #         res['discount_type'] = self.discount_type
    #         res['discount_value'] = self.discount_value
    #
    #     return res

    # @api.one
    @api.depends('order_line.price_subtotal', 'discount_type', 'discount_value')
    def disc_amount(self):
        # orginal for V8
        # val = 0
        # for line in self.order_line:
        #     val += self._amount_line_tax(line)

        for obj in self:
            if obj.discount_view == 'After Tax':
                if obj.discount_type == 'Fixed':
                    obj.discounted_amount = obj.discount_value
                elif obj.discount_type == 'Percentage':
                    # original on V8
                    # amount_to_dis = (self.amount_untaxed + val) * (self.discount_value / 100)

                    # adapt for v9
                    # แก้ไข
                    amount_to_dis = (obj.amount_untaxed + obj.amount_tax) * (obj.discount_value / 100)
                    obj.discounted_amount = round(amount_to_dis, 2)
                else:
                    obj.discounted_amount = 0
            elif obj.discount_view == 'Before Tax':
                if obj.discount_type == 'Fixed':
                    obj.discounted_amount = obj.discount_value
                elif obj.discount_type == 'Percentage':
                    amount_to_dis = obj.amount_untaxed * (obj.discount_value / 100)
                    obj.discounted_amount = round(amount_to_dis, 2)
                else:
                    obj.discounted_amount = 0
            else:
                obj.discounted_amount = 0

SaleOrder_inherit()


class SaleOrderLine(models.Model):
    _inherit ='sale.order.line'

    discount_amount = fields.Float('Discount (Amount)', default=0.0)


    def get_lines(self, data, max_line):
        # this function will count number of \n
        # print  data
        line_count = data.count("\n")
        if not line_count:
            #  print "line 0 - no new line or only one line"
            # lenght the same with line max
            if not len(data) % max_line:
                line_count = len(data) / max_line
            # lenght not the same with line max
            # if less than line max then will be 0 + 1
            # if more than one, example 2 line then will be 1 + 1
            else:
                line_count = len(data) / max_line + 1
        elif line_count:
            # print "line not 0 - has new line"
            # print line_count
            # if have line count mean has \n then will be add 1 due to the last row have not been count \n
            line_count += 1
            data_line_s = data.split('\n')
            for x in range(0, len(data_line_s), 1):
                # print data_line_s[x]
                if len(data_line_s[x]) > max_line:
                    # print "more than one line"
                    line_count += len(data_line_s[x]) / max_line
        return line_count

        # option discount amount per unit or price sub total

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'discount_amount')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            if line.discount_amount > 0.0:
                if self.env.user.company_id.discount_amount_condition and self.env.user.company_id.discount_amount_condition == 'unit':
                    price -= line.discount_amount
                else:
                    price -= line.discount_amount / line.product_uom_qty

            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                            product=line.product_id, partner=line.order_id.partner_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    @api.onchange('product_id')
    def product_id_change(self):
        domain = super(SaleOrderLine, self).product_id_change()
        if self.product_id:
            vals = {}
            vals['name'] = self.product_id.name
            self.update(vals)

        return domain


