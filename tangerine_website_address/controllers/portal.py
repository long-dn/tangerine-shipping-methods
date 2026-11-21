from odoo import _
from odoo.http import request, route
from odoo.addons.portal.controllers.portal import CustomerPortal


class CustomerPortalModesk(CustomerPortal):

    def _get_mandatory_address_fields(self, country_sudo):
        required_fields = super()._get_mandatory_address_fields(country_sudo)
        if country_sudo.code == 'VN':
            required_fields.discard('city')
            required_fields.add('state_id')
            required_fields.add('ward_id')
        return required_fields

    def _prepare_address_form_values(self, partner_sudo, *args, **kwargs):
        rendering_values = super()._prepare_address_form_values(partner_sudo, *args, **kwargs)
        partner_sudo = rendering_values.get('partner_sudo')
        if not partner_sudo:
            partner_sudo = rendering_values.get('current_partner').sudo()
        if partner_sudo.country_id.code == 'VN':
            rendering_values.update({
                'ward_id': partner_sudo.ward_id.id,
                'state_wards': partner_sudo.state_id.ward_ids,
            })
        return rendering_values

    @route(
        route='/my/address/state_vn_info/<model("res.country.state"):state>',
        type='jsonrpc',
        auth='public',
        methods=['POST'],
        website=True,
        readonly=True
    )
    def state_infos(self, state, **kw):
        return {
            'wards': [(w.id, w._vietnamese_address_name(), w.code) for w in state.sudo().ward_ids
                      if state.active and state.country_id.code == 'VN']
        }

    def _validate_address_values(self, address_values, *args, **kwargs):
        country_id = address_values.get('country_id')
        if country_id and country_id != request.env.ref('base.vn').id:
            address_values['ward_id'] = False
        invalid, missing, messages = super()._validate_address_values(address_values, *args, **kwargs)
        ward_id = address_values.get('ward_id')
        if ward_id:
            ward = (request.env['res.country.ward'].sudo().browse(ward_id).exists()
                    if isinstance(ward_id, int) else False)
            if not ward or not ward.active or ward.state_id.id != address_values.get('state_id'):
                invalid.add('ward_id')
                messages.append(_('Select a ward belonging to the chosen province.'))
        return invalid, missing, messages
