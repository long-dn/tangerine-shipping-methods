from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for xmlid, old_path, new_path in (
        ('ntl_create_bill', '/v2/bill/create', '/v3/bill/create'),
        ('ntl_calculate_price', '/v1/bill/calc-fee', '/v3/bill/calc-fee'),
    ):
        route = env.ref('tangerine_delivery_nhat_tin.' + xmlid, raise_if_not_found=False)
        if route and route.route == old_path:
            route.route = new_path
