# -*- coding: utf-8 -*-
# Copyright (C) 2016-2017  ITtaas.
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from dateutil.rrule import (YEARLY,MONTHLY,WEEKLY,DAILY)
from datetime import datetime, timedelta, date
from pytz import timezone
import pytz
import calendar

import uuid

from datetime import datetime, timedelta

strptime = datetime.strptime
strftime = datetime.strftime


class ir_sequence_inherit(models.Model):
    _inherit = "ir.sequence"


    def action_gen_seq(self):
        # print("seq_____________________")

        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            compose_form_id = ir_model_data.get_object_reference('itaas_generate_sequence', 'ir_sequence_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_res_id': self.id,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'ir.sequence.wizard',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def action_del_seq(self):
        # print("seq_____________________")

        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            compose_form_id = ir_model_data.get_object_reference('itaas_generate_sequence', 'ir_sequence_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_res_id': self.id,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'ir.sequence.wizard',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }


class ir_sequence_wizard(models.Model):
    _name = 'ir.sequence.wizard'

    res_id = fields.Integer('Related Document ID', index=True)
    start_year = fields.Selection([(str(num), str(num)) for num in range((datetime.now().year-5), (datetime.now().year) + 10)], string='From Year',default=(datetime.now().year))
    to_year = fields.Selection([(str(num), str(num)) for num in range((datetime.now().year-5), (datetime.now().year) + 10)], string='To Year',default=(datetime.now().year))
    type_range = fields.Selection([('day', 'Day'), ('month', 'Month'),],string="Type Range",default='month')

    @api.model
    def default_get(self, fields):
        res = super(ir_sequence_wizard, self).default_get(fields)
        print("default_get_________________________")
        print(dict(self.env.context or {}))
        res_id = self._context.get('default_res_id')
        self.update({'res_id': res_id,})
        return res

    def action_delete(self):
        res_ids = self.env["ir.sequence.date_range"].sudo().search([('sequence_id', '=', self.res_id),('number_next','=',1),('date_from', '>=', datetime(int(self.start_year), 1, 1)),('date_to', '<=', datetime(int(self.to_year), 12, 31))])
        # print ('---ReS--')
        # print (res_ids)
        res_ids.unlink()

    def action_gen(self):
        """
        Create seq
        """
        res_id = self.env["ir.sequence"].sudo().search([('id', '=', self.res_id)])
        if self.start_year > self.to_year:
            raise UserError(_('From year shoud not less than To year.'))
        else:
            # for fy in res_id:
            #     for date in fy.date_range_ids:
            #         date.unlink()
            #     fy.refresh()

            if self.type_range == 'month':
                # # for range month version
                for year in range(int(self.start_year),  int(self.to_year) + 1):
                    for month in range(0, 12, 1):
                        if month < 11:
                            val = {
                                'date_from': datetime(year, month+1, 1),
                                'date_to': datetime(year, month+2, 1) - relativedelta(days=1),
                                'number_next_actual': 1,
                            }
                        else:
                            val = {
                                'date_from': datetime(year, month + 1, 1),
                                'date_to': datetime(year+1, 1, 1) - relativedelta(days=1),
                                'number_next_actual': 1,
                            }
                        print(val)
                        res_id.write({
                            'date_range_ids': [(0, 0, val)],
                        })
            else:
                # # for range day version
                begin_year = datetime.strptime(str(self.start_year)+",1,1", "%Y,%m,%d")
                end_year = datetime.strptime(str(self.to_year)+",12,31", "%Y,%m,%d")
                range_year = (end_year - begin_year).days
                for day in range(0, range_year+1):
                    val = {
                        'date_from': datetime(begin_year.year, 1, 1) + relativedelta(days=day),
                        'date_to':datetime(begin_year.year, 1, 1) + relativedelta(days=day),
                        'number_next_actual': 1,
                    }
                    res_id.write({
                        'date_range_ids': [(0, 0, val)],
                    })






