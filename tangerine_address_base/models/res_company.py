from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    district_id = fields.Many2one('res.country.district', string='District',
                                  domain="[('state_id','=', state_id)]")

    ward_id = fields.Many2one('res.country.ward', string='Ward',
                              domain="[('state_id', '=', state_id)]")

    @api.onchange('state_id', 'country_id')
    def _onchange_vietnam_ward(self):
        if self.ward_id and (self.ward_id.state_id != self.state_id or self.state_id.country_id != self.country_id):
            self.ward_id = False
