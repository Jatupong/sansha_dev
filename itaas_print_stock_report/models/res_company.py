# -*- coding: utf-8 -*-
from openerp import fields, api, models, _
from bahttext import bahttext
from openerp.exceptions import UserError
from datetime import datetime, date

class res_company(models.Model):
    _inherit ="res.company"




