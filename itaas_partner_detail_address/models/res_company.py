# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from odoo import fields, api, models, _

class res_company(models.Model):
    _inherit ="res.company"

    fax = fields.Char(String='Fax')
    eng_name = fields.Char(string="Company English Name")