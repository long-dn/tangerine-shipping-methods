# -*- coding: utf-8 -*-
import re
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Partner(models.Model):
    _inherit = 'res.partner'

    # outdated
    district_id = fields.Many2one(
        comodel_name='res.country.district',
        string='District',
        domain="[('state_id','=', state_id)]"
    )
    ward_id = fields.Many2one(
        comodel_name='res.country.ward',
        string='Ward/Commune',
        domain="[('state_id', '=', state_id)]"
    )
    full_address = fields.Char(compute='_compute_address_structure')

    @api.depends('country_id', 'state_id', 'ward_id', 'street')
    def _compute_address_structure(self):
        self.full_address = False
        for rec in self:
            if rec.country_id and rec.country_id.code == 'VN':
                address_parts = [
                    rec.street,
                    rec.ward_id.display_name,
                    rec.state_id.display_name,
                    rec.country_id.display_name
                ]
                rec.full_address = ', '.join(filter(None, address_parts))

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
