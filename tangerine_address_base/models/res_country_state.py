import re
from odoo import models, fields, api


class CountryState(models.Model):
    _inherit = 'res.country.state'
    _order = 'code_ext'

    def _make_code_ext(self):
        for record in self:
            if not record.code_ext:
                record.code_ext = record.code

    code_ext = fields.Char(string='Legacy State Code', required=True, compute=_make_code_ext, store=True)
    district_ids = fields.One2many('res.country.district', 'state_id')

    active = fields.Boolean(default=True)
    external_code = fields.Char(string='External Code')
    state_type = fields.Selection([
        ('province', 'Province'), ('city', 'City'), ('capital', 'Capital'),
    ], default='province')
    ward_ids = fields.One2many('res.country.ward', 'state_id')

    @api.model
    def _archive_merged_vietnam_states(self, codes):
        states = self.search([('country_id', '=', self.env.ref('base.vn').id), ('code', 'in', codes)])
        states.write({'active': False})
