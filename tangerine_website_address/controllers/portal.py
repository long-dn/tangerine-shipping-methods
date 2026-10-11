from odoo.http import route
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
            'wards': [{'id': w.id, 'name': w.name} for w in state.sudo().ward_ids]
        }
