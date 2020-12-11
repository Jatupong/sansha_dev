# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from bahttext import bahttext
from odoo.exceptions import UserError
from datetime import datetime, date

class res_partner(models.Model):
    _inherit ="res.partner"

    is_sale_report = fields.Boolean('Show Sale Report')