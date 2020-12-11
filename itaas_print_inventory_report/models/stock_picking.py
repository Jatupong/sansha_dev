from odoo import fields, api, models, _
from bahttext import bahttext
from odoo.exceptions import UserError
from datetime import datetime, date


class StockPicking_inherit(models.Model):
    _inherit = "stock.picking"

    notes = fields.Text('Note')

    def get_lines(self, data, max_line):
        print ('-xxx')
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
        # print("final line")
        # print(line_count)
        return line_count

    def get_break_line(self, max_body_height, new_line_height, row_line_height, max_line_lenght):
        break_page_line = []
        count_height = 0
        count = 1
        # move_line_ids = []
        # for move in self.move_lines:
        #     move_line_ids.append(move.move_line_ids.ids)
        #
        # print (move_line_ids)
        # print ('-----------xxxx')
        for line in self.move_lines:

            # count += 1
            print(count)
            print(line.product_id.default_code)
            print(line.name)

            line_name = self.get_lines(line.product_id.name, max_line_lenght)
            line_move_line_ids = len(line.move_line_ids)
            print("line_move_line_ids")
            print(len(line.move_line_ids))

            if (line_name > line_move_line_ids):
                line_height = row_line_height + ((line_name) * new_line_height)
            else:
                line_height = row_line_height + ((line_move_line_ids) * new_line_height)

            count_height += line_height
            if count_height > max_body_height:
                break_page_line.append(count - 1)
                count_height = line_height
            count += 1
        # last page
        break_page_line.append(count - 1)

        print('######################################3')
        print(break_page_line)
        return break_page_line

    def baht_text(self, amount_total):
        return bahttext(amount_total)

    def get_break_line_02(self, max_body_height, new_line_height, row_line_height, max_line_lenght):
        break_page_line = []
        count_height = 0
        count = 1
        line_default_code = 0

        # print('get_break_line_02:', break_page_line)
        # for line in self.move_lines.filtered(lambda x: x.quantity_done > 0.0):
        for line in self.move_lines:

            # count += 1
            # print(count)
            # print(line.product_id.default_code)
            # print(line.name)
            if(line.product_id.default_code):
                line_default_code = self.get_lines(line.product_id.default_code, 15)
            line_name = self.get_lines(line.product_id.name, max_line_lenght)

            line_move_line_ids_lot_name = len(line.move_line_ids.filtered(lambda c: c.lot_name))
            line_move_line_ids_lot_id = len(line.move_line_ids.filtered(lambda c: c.lot_id))

            if (line_move_line_ids_lot_name >= line_move_line_ids_lot_id):
                line_move_line_ids = line_move_line_ids_lot_name
            else:
                line_move_line_ids = line_move_line_ids_lot_id

            if (line_default_code > line_name and line_default_code > line_move_line_ids):
                # print("1")
                get_line = line_default_code
            elif (line_name > line_default_code and line_name > line_move_line_ids):
                # print("2")
                get_line = line_name
            # if (line_move_line_ids > line_default_code and line_move_line_ids > line_name):
            else:
                get_line = line_move_line_ids
                # print("3")

            print("get_line")
            print(get_line)
            line_height = row_line_height + ((get_line) * new_line_height)
            print("line_height")
            print(line_height)
            count_height += line_height
            if count_height > max_body_height:
                break_page_line.append(count - 1)
                count_height = line_height
            count += 1
        # last page
        break_page_line.append(count - 1)

        print(break_page_line)
        return break_page_line



    def get_break_line_without_package(self, max_body_height, new_line_height, row_line_height, max_line_lenght):
        break_page_line = []
        count_height = 0
        count = 1
        line_default_code = 0

        # print('get_break_line_02:', break_page_line)
        # for line in self.move_lines.filtered(lambda x: x.quantity_done > 0.0):
        for line in self.move_line_ids:

            # count += 1
            # print(count)
            # print(line.product_id.default_code)
            # print(line.name)
            if(line.product_id.default_code):
                line_default_code = self.get_lines(line.product_id.default_code, 15)
            line_name = self.get_lines(line.product_id.name, max_line_lenght)

            if (line_default_code > line_name):
                # print("1")
                get_line = line_default_code
            else:
                get_line = line_name
                # print("3")

            print("get_line")
            print(get_line)
            line_height = row_line_height + ((get_line) * new_line_height)
            print("line_height")
            print(line_height)
            count_height += line_height
            if count_height > max_body_height:
                break_page_line.append(count - 1)
                count_height = line_height
            count += 1
        # last page
        break_page_line.append(count - 1)

        print(break_page_line)
        return break_page_line

    def get_break_line_04(self, max_body_height, new_line_height, row_line_height, max_line_lenght):
        break_page_line = []
        count_height = 0
        count = 1

        for line in self.move_lines:

            if line.product_id.default_code:
                product = "[" + line.product_id.default_code + "]" + line.product_id.name
            else:
                product = line.product_id.name

            get_line = self.get_lines(product, max_line_lenght)

            line_height = row_line_height + ((get_line) * new_line_height)

            count_height += line_height
            if count_height > max_body_height:
                break_page_line.append(count - 1)
                count_height = line_height
            count += 1
        # last page
        break_page_line.append(count - 1)

        print(break_page_line)
        return break_page_line


    def get_origin(self, origin):

        obj_origin = self.env['material.purchase.requisition'].search(
            [('sequence', '=', origin)], limit=1)
        product_name = obj_origin.mo_id.product_id.name
        product_id = obj_origin.mo_id.product_id.default_code
        print("---------")
        print("[" + product_id + "]" + product_name)
        return "[" + product_id + "] " + product_name

    def address_custom(self, object):
        active = False
        object_name = str(object).split('(')
        object_name = object_name[0]
        ir_models = self.env['report.address.custom'].search([('model_access.model', '=', object_name)], limit=1)
        if ir_models:
            active = True
        return active, ir_models


class StockMove_inherit(models.Model):
    _inherit = "stock.move"

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
        # print("final line")
        # print(line_count)
        return line_count

    def get_break_line(self, max_body_height, new_line_height, row_line_height, max_line_lenght):
        break_page_line = []
        count_height = 0
        count = 1
        # move_line_ids = []
        # for move in self.move_lines:
        #     move_line_ids.append(move.move_line_ids.ids)
        #
        # print (move_line_ids)
        # print ('-----------xxxx')
        for line in self.move_line_ids:

            # count += 1
            print(count)
            print(line.product_id.default_code)
            # print(line.name)

            line_name = self.get_lines(line.product_id.name, max_line_lenght)
            # line_move_line_ids = len(line.move_line_ids)
            # print("line_move_line_ids")
            # print(len(line.move_line_ids))


            line_height = row_line_height + ((line_name) * new_line_height)


            count_height += line_height
            if count_height > max_body_height:
                break_page_line.append(count - 1)
                count_height = line_height
            count += 1
        # last page
        break_page_line.append(count - 1)

        print('######################################3')
        print(break_page_line)
        return break_page_line
