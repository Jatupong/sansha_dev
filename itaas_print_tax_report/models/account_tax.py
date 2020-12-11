# -*- coding: utf-8 -*-
# Copyright (C) 2016-2017  Technaureus Info Solutions(<http://technaureus.com/>).

from odoo import api, fields, models, _

class Account_Tax(models.Model):
    _inherit = 'account.tax'

    wht_personal_company = fields.Selection([('personal', 'ภงด3'), ('company', 'ภงด53'),('pnd1_kor', 'ภงด1ก'),('pnd1_kor_special', 'ภงด1ก พิเศษ'),('pnd2', 'ภงด2'),('pnd2_kor', 'ภงด2ก'),('personal_kor', 'ภงด3ก')])