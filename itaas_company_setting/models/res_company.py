# -*- coding: utf-8 -*-
from openerp import fields, api, models, _
from bahttext import bahttext
from openerp.exceptions import UserError
from datetime import datetime, date

class ResCompany(models.Model):
    _inherit ="res.company"

    system_version = fields.Char(string='System Version', default='13.0.1')
    release_date = fields.Date(string='Release Date',default='2020-07-01')