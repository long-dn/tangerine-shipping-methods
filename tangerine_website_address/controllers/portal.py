from odoo import _
from odoo.http import request, route
from odoo.addons.portal.controllers.portal import CustomerPortal


class CustomerPortalModesk(CustomerPortal):

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
            'wards': [{'id': w.id, 'name': w._vietnamese_address_name()} for w in state.sudo().ward_ids
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
