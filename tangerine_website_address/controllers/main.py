import json

from odoo import _, http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


def validate_ward(values, errors, messages):
    if str(values.get('country_id')) != str(request.env.ref('base.vn').id):
        values['ward_id'] = False
        return
    ward_id = str(values.get('ward_id', ''))
    ward = request.env['res.country.ward'].sudo().browse(int(ward_id)).exists() if ward_id.isdecimal() else False
    if not ward or not ward.active or str(ward.state_id.id) != str(values.get('state_id')):
        errors['ward_id'] = 'error'
        messages.append(_('Select a ward belonging to the chosen province.'))
    else:
        values['ward_id'] = ward.id


class WebsiteSaleAddress(WebsiteSale):

    def _vietnam_required_fields(self, fields, country_id):
        if str(country_id) == str(request.env.ref('base.vn').id):
            return list(dict.fromkeys([f for f in fields if f != 'city'] + ['state_id', 'ward_id']))
        return fields

    def _get_mandatory_fields_billing(self, country_id=False):
        fields = super()._get_mandatory_fields_billing(country_id)
        return self._vietnam_required_fields(fields, country_id)

    def _get_mandatory_fields_shipping(self, country_id=False):
        fields = super()._get_mandatory_fields_shipping(country_id)
        return self._vietnam_required_fields(fields, country_id)

    @http.route('/shop/vietnam/wards/<int:state_id>', type='http', auth='public', methods=['GET'], website=True)
    def vietnam_wards(self, state_id):
        wards = request.env['res.country.ward'].sudo().search([
            ('state_id', '=', state_id), ('state_id.country_id', '=', request.env.ref('base.vn').id),
            ('state_id.active', '=', True),
        ])
        return request.make_response(
            json.dumps([(ward.id, ward._vietnamese_address_name()) for ward in wards], ensure_ascii=False),
            headers=[('Content-Type', 'application/json; charset=utf-8')],
        )

    def values_preprocess(self, *args):
        values = dict(args[-1])
        ward_id = str(values.get('ward_id', ''))
        values['ward_id'] = int(ward_id) if ward_id.isdecimal() else False
        return super().values_preprocess(*args[:-1], values)

    def values_postprocess(self, order, mode, values, errors, error_msg):
        post, errors, error_msg = super().values_postprocess(order, mode, values, errors, error_msg)
        validate_ward(values, errors, error_msg)
        post['ward_id'] = values.get('ward_id', False)
        post.pop('district_id', None)
        return post, errors, error_msg
