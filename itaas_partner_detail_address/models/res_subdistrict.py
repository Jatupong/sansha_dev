# -*- coding: utf-8 -*-
# Copyright (C) 2019-Today  Technaureus Info Solutions(<http://technaureus.com/>).

from odoo import api, fields, models
from odoo.osv import expression


class ResSubDistrict(models.Model):
    _name = "res.sub.district"
    _description = "Sub District"

    district_id = fields.Many2one('res.district', string='District', required=True)
    name = fields.Char(string='Sub District Name', required=True)
    code = fields.Char(string='Sub District Code', help='The sub district code.', required=True)
    zip = fields.Char(string='Zip Code', help='The sub district code.', required=True)

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('code', operator, name)]
        sub_district_ids = self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
        return models.lazy_name_get(self.browse(sub_district_ids).with_user(name_get_uid))
