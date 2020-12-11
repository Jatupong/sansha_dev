# -*- coding: utf-8 -*-
from openerp import fields, api, models, _
from bahttext import bahttext

class CustomerBilling(models.Model):
    _inherit ="customer.billing"


    def get_report_amount(self):
        print ('get_report_amount')
        amount_ids = []
        sum_untaxed_amount = 0
        sum_discounted_amount = 0
        sum_after_discounted_amount = 0
        sum_tax_amount = 0
        sum_total_amount = 0
        if self.invoice_ids:
            for invoice in self.invoice_ids:
                if invoice.type == 'out_invoice':
                    sum_untaxed_amount += invoice.amount_untaxed
                    sum_discounted_amount += invoice.discount_value
                    sum_tax_amount += invoice.amount_tax
                    sum_total_amount += invoice.amount_total
                else:
                    sum_untaxed_amount -= invoice.amount_untaxed
                    sum_discounted_amount -= invoice.discount_value
                    sum_tax_amount -= invoice.amount_tax
                    sum_total_amount -= invoice.amount_total
            sum_after_discounted_amount = sum_untaxed_amount - sum_discounted_amount

        amount_ids.append(abs(sum_untaxed_amount))
        amount_ids.append(abs(sum_discounted_amount))
        amount_ids.append(abs(sum_after_discounted_amount))
        amount_ids.append(abs(sum_tax_amount))
        amount_ids.append(abs(sum_total_amount))

        return amount_ids


    def baht_text(self, amount_total):
        return bahttext(amount_total)


    def get_line(self, data, max_line):
        # this function will count number of \n
        line_count = data.count("\n")
        if not line_count:
            # print "line 0 - no new line or only one line"
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
        for line in self.invoice_ids:
            line_name = self.get_lines(line.number, max_line_lenght)
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

        print(break_page_line)
        return break_page_line

    def get_break_line_invoice(self, max_body_height, new_line_height, row_line_height, max_line_lenght):
        break_page_line = []
        count_height = 0
        count = 1
        # print 'get_break_line_invoice'
        for line in self.invoice_ids:
            line_name = self.get_line(line.name, max_line_lenght)
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
        # print "break_page_line"
        # print break_page_line
        return break_page_line


