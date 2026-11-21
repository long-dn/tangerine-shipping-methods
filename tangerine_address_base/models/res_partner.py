# -*- coding: utf-8 -*-
import re
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Partner(models.Model):
    _inherit = 'res.partner'

    district_id = fields.Many2one(comodel_name='res.country.district', string='District',
                                  domain="[('state_id','=', state_id)]")
    ward_id = fields.Many2one(comodel_name='res.country.ward', string='Ward',
                              domain="[('state_id', '=', state_id)]")

    shipping_address = fields.Char(compute='_compute_complete_shipping_address')

    @staticmethod
    def replace_address_name(pattern, name):
        for long_text, short_text in pattern.items():
            name = re.sub(long_text, short_text, name, flags=re.IGNORECASE)
        return name

    @staticmethod
    def replace_province_text(name):
        return re.sub(r'\btp\s+', '', name, flags=re.IGNORECASE)

    @api.depends('street', 'ward_id', 'state_id')
    def _compute_complete_shipping_address(self):
        for record in self:
            record.shipping_address = ''
            if record.street:
                record.shipping_address += record.street + ', '
            if record.ward_id:
                pattern = {r'\bphường\s+': 'P.', r'\bxã\s+': 'X.', r'\bthị\s+trấn\s+': 'TT.', r'\bhuyện\s+': 'H.'}
                record.shipping_address += self.replace_address_name(pattern, record.ward_id._vietnamese_address_name()) + ', '
            if record.state_id:
                record.shipping_address += self.replace_province_text(record.state_id.name) + ', '
            record.shipping_address = record.shipping_address.strip().strip(',')

    @api.model
    def _address_fields(self):
        return super()._address_fields() + ['ward_id']

    @api.onchange('state_id', 'country_id')
    def _onchange_vietnam_ward(self):
        if self.ward_id and (self.ward_id.state_id != self.state_id or self.state_id.country_id != self.country_id):
            self.ward_id = False

    @api.constrains('ward_id', 'state_id', 'country_id')
    def _check_vietnam_ward(self):
        for partner in self.filtered('ward_id'):
            if (partner.ward_id.state_id != partner.state_id
                    or partner.state_id.country_id != partner.country_id):
                raise ValidationError(_('The ward must belong to the selected province and country.'))
