import csv
import logging
from pathlib import Path

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    cr.execute("""
        SELECT d.name, w.id, w.code FROM ir_model_data d
          JOIN res_country_ward w ON w.id = d.res_id
         WHERE d.module = 'tangerine_address_base' AND d.model = 'res.country.ward'
           AND d.name ~ '^res_ward_[0-9]+$'
    """)
    legacy = {name: (rid, code) for name, rid, code in cr.fetchall()}
    # 202/2025/QH15. Only move province-only addresses here. A split ward
    # keeps its original province until the customer selects the new address.
    partners = env['res.partner'].with_context(active_test=False)
    for target_code, source_codes in (
        ('SG', ('43', '57')), ('56', ('54',)), ('69', ('53',)),
        ('59', ('55',)), ('39', ('58',)), ('35', ('40', '72')),
        ('49', ('50', '51')), ('30', ('31',)), ('68', ('14', '70')),
        ('HP', ('61',)), ('CT', ('52', '73')), ('07', ('03',)),
        ('18', ('63', '67')), ('44', ('47',)), ('29', ('28',)),
        ('37', ('41',)), ('34', ('36',)), ('33', ('32',)),
        ('25', ('24',)), ('DN', ('27',)), ('66', ('20',)),
        ('45', ('46',)), ('02', ('06',)),
    ):
        target = env.ref('base.state_vn_VN-' + target_code)
        addresses = partners.search([
            ('ward_id', '=', False), ('state_id.country_id', '=', target.country_id.id),
            ('state_id.code', 'in', ['VN-' + code for code in source_codes]),
        ])
        addresses._update_address({'state_id': target.id})
        addresses.write({'district_id': False})
    cr.execute("""
        SELECT res_id FROM ir_model_data
         WHERE module = 'tangerine_address_base' AND model = 'res.country.district'
           AND name ~ '^res_district_[0-9]+$'
    """)
    env['res.country.district'].browse([rid for rid, in cr.fetchall()]).exists().write({'active': False})
    if not legacy:
        return
    cr.execute("""
        SELECT w.code, w.id FROM res_country_ward w
          JOIN ir_model_data d ON d.res_id = w.id
         WHERE d.module = 'tangerine_address_base' AND d.model = 'res.country.ward'
           AND d.name ~ '^ward_vn_[0-9]+$'
    """)
    current = dict(cr.fetchall())
    successor = {}
    with Path(__file__).with_name('ward_successors.csv').open(encoding='utf-8') as stream:
        for row in csv.DictReader(stream):
            old = legacy.get(row['old_xmlid'])
            if old and old[1] == row['old_code']:
                successor[old[0]] = current[row['new_code']]

    wards = env['res.country.ward']
    old_ids = [rid for rid, code in legacy.values()]
    for model in ('res.partner', 'res.company'):
        records = env[model].with_context(active_test=False)
        if not records._fields['ward_id'].store:
            continue  # Computed company addresses follow their partner.
        pending = 0
        for address in records.search([('ward_id', 'in', old_ids)]):
            old = address.ward_id
            target = successor.get(old.id)
            ward = wards.browse(target)
            if (not target or (address.state_id and address.state_id not in (old.state_id, ward.state_id))
                    or (address.country_id and address.country_id != old.state_id.country_id)):
                pending += 1
                continue
            values = {'ward_id': ward.id, 'state_id': ward.state_id.id,
                      'country_id': ward.state_id.country_id.id}
            if model == 'res.partner':
                address._update_address(values)
                address.write({'district_id': False})
            else:
                address.write(dict(values, district_id=False))
        if pending:
            _logger.warning('%s: %s historical addresses need manual ward selection', model, pending)
    wards.browse(old_ids).write({'active': False})
