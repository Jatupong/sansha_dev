# -*- coding: utf-8 -*-
from openerp import fields, api, models
from bahttext import bahttext

class ResBank_inherit(models.Model):
    # _name = "res.bank.in"
    _inherit = "res.bank"

    layout_name_top = fields.Integer('top',default=87)
    layout_name_left = fields.Integer('left',default=140)
    layout_name_show = fields.Boolean('show',default=True)

    layout_amount_top = fields.Integer('top', default=160)
    layout_amount_left = fields.Integer('left', default=515)
    layout_amount_show = fields.Boolean('show', default=True)

    layout_baht_top = fields.Integer('top', default=125)
    layout_baht_left = fields.Integer('left', default=150)
    layout_baht_show = fields.Boolean('show',default=True)

    layout_date_top = fields.Integer('top', default=20)
    layout_date_left = fields.Integer('left', default=600)
    layout_date_show = fields.Boolean('show',default=True)

    layout_partner_top = fields.Integer('top', default=87)
    layout_partner_left = fields.Integer('left', default=140)
    layout_partner_show = fields.Boolean('show',default=False)
