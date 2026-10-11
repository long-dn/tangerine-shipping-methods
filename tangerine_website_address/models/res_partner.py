from odoo import models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _get_mandatory_address_fields(self, country_sudo, **kwargs):
        field_names = super()._get_mandatory_address_fields(country_sudo, **kwargs)
        if country_sudo.code == 'VN':
            field_names |= {'state_id', 'ward_id'}
        return field_names
