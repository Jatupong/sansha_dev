# -*- coding: utf-8 -*-
# Copyright (C) 2020-today ITAAS (Dev K.Book)

from odoo import fields, api, models, _
from odoo.exceptions import UserError, ValidationError

class res_partner(models.Model):
    _inherit = "res.partner"


    @api.constrains('vat')
    def _check_vat_unique(self):
        # This constraint could possibly underline flaws in bank statement import (eg. inability to
        # support hacks such as using dummy transactions to give additional informations)

        for partner in self:
            if partner.vat:
                cr = self._cr
                cr.execute('SELECT id FROM res_partner WHERE vat = %s and parent_id is Null', (partner.vat,))
                res = cr.fetchall()
                if len(res) > 1 and partner.vat != '':
                    raise ValidationError(_('หมายเลข Tax ID %s มีอยู่แล้ว') % partner.vat)