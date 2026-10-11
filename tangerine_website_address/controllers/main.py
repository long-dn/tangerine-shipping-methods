from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleModesk(WebsiteSale):

    def _get_mandatory_address_fields(self, country_sudo):
        required_fields = super()._get_mandatory_address_fields(country_sudo)
        if country_sudo.code == 'VN':
            required_fields.add('state_id')
            required_fields.add('ward_id')
        return required_fields

    def _prepare_address_form_values(self, order_sudo, partner_sudo, *args, **kwargs):
        rendering_values = super()._prepare_address_form_values(order_sudo, partner_sudo, *args, **kwargs)
        if partner_sudo.country_id.code == 'VN':
            rendering_values.update({
                'ward_id': partner_sudo.ward_id.id,
                'state_wards': partner_sudo.state_id.ward_ids,
            })
        return rendering_values
