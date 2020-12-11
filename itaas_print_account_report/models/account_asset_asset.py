import time
from odoo import api, models, fields
from datetime import datetime,timedelta,date
from dateutil.relativedelta import relativedelta
import calendar
import dateutil.parser
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT
import locale

class AccountAssetAssetLine(models.Model):
    _name = 'asset.location.line'
    _rec_name = 'name'
    _order = 'id desc'

    name = fields.Char('Name')
    date_asset = fields.Date('วันที่ Asset')
    asset_line = fields.Many2one('account.asset.asset', string="Asset Line")
    location_old = fields.Many2one('assets.location',string="Location Old")
    location_new = fields.Many2one('assets.location', string="Location New")


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    @api.model
    def create(self, vals):
        request = super(AccountAssetAsset, self).create(vals)
        request.write({'number': self.env['ir.sequence'].next_by_code('Cash.register'), })

        return request

    number = fields.Char(string='Number')
    date_asset = fields.Date('วันที่ Asset')
    location_ids = fields.One2many('asset.location.line', 'asset_line', string='Location')
    location_new = fields.Many2one('assets.location', string="Location New")

    @api.onchange('location_new','date_asset')
    def onchange_location(self):
        print('111')
        print(self.location_asset)
        if self.location_asset and self.location_new:
            test = self.location_asset
            print(test)
            location_idz = []
            for asset in self:
                vals = {
                    'name': self.name,
                    'location_old': asset.location_asset,
                    'location_new': asset.location_new,
                    'date_asset': asset.date_asset,
                }
                location_idz.append((0, 0, vals))
                print(location_idz)
            self.update({'location_ids': location_idz})

        elif not self.location_asset and self.location_new:
            print('222222222')
            location_idz = []
            for asset in self:
                vals = {
                    'name': self.name,
                    # 'location_old': asset.location_asset,
                    'location_new': asset.location_new,
                }
                location_idz.append((0, 0, vals))
                print(location_idz)
            self.update({'location_ids': location_idz})

    # @api.multi
    # def location(self):
    #     if self.location_asset:
    #         location_idsz = []
    #         for asset12 in self:
    #             vals = {
    #                 'name': asset12.name,
    #                 'location_old': asset12.location_asset.id,
    #                 'location_new': asset12.location_asset.id,
    #             }
    #             print(vals)
    #             location_idsz.append((0, 0, vals))
    #             self.update({'location_ids': location_idsz})


#
#




