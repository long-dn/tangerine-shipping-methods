from odoo.http import request, route
from odoo.addons.portal.controllers.portal import CustomerPortal


class CustomerPortalModesk(CustomerPortal):

    @staticmethod
    def _to_record_id(value):
        return int(value) if value and str(value).isdigit() else False

    def _is_vn_portal_form(self):
        # set by details_form_validate from the posted country, see l10n_mx
        country_id = self._to_record_id(request.env.context.get('portal_form_country_id'))
        return bool(country_id) and request.env['res.country'].sudo().browse(country_id).code == 'VN'

    def _get_mandatory_fields(self):
        mandatory_fields = super()._get_mandatory_fields()
        if self._is_vn_portal_form():
            mandatory_fields += [fname for fname in ('state_id', 'ward_id') if fname not in mandatory_fields]
        return mandatory_fields

    def _get_optional_fields(self):
        optional_fields = super()._get_optional_fields()
        if 'ward_id' not in optional_fields:
            optional_fields += ['ward_id']
        return optional_fields

    def details_form_validate(self, data, partner_creation=False):
        error, error_message = super().details_form_validate(data, partner_creation=partner_creation)
        if 'ward_id' in data:
            # the account route only converts country_id and state_id to ids
            data['ward_id'] = self._to_record_id(data['ward_id'])
        return error, error_message

    @route()
    def account(self, redirect=None, **post):
        response = super().account(redirect=redirect, **post)
        qcontext = getattr(response, 'qcontext', None)
        if qcontext and qcontext.get('partner'):
            partner_sudo = qcontext['partner'].sudo()
            state_id = self._to_record_id(qcontext.get('state_id'))
            state_sudo = request.env['res.country.state'].sudo().browse(state_id) if state_id else partner_sudo.state_id
            vn_country = request.env.ref('base.vn')
            qcontext.update({
                'vn_country_id': vn_country.id,
                'state_wards': state_sudo.ward_ids if state_sudo.country_id == vn_country else [],
            })
        return response

    @route(
        route='/my/address/state_vn_info/<model("res.country.state"):state>',
        type='json',
        auth='public',
        methods=['POST'],
        website=True,
        readonly=True
    )
    def state_vn_infos(self, state, **kw):
        return {
            'wards': [(w.id, w.name, w.code) for w in state.sudo().ward_ids]
        }
