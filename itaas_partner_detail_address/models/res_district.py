# -*- coding: utf-8 -*-
# Copyright (C) 2019-Today  Technaureus Info Solutions(<http://technaureus.com/>).

from odoo import api, fields, models
from odoo.osv import expression


class ResDistrict(models.Model):
    _name = "res.district"
    _description = "District"

    state_id = fields.Many2one('res.country.state', string='State', required=True)
    name = fields.Char(string='District Name', required=True)
    code = fields.Char(string='District Code', help='The district code.', required=True)

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('code', operator, name)]
        district_ids = self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
        return models.lazy_name_get(self.browse(district_ids).with_user(name_get_uid))