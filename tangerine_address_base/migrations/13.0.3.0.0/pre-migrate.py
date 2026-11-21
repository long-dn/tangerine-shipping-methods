def migrate(cr, version):
    # Preserve legacy rows even when Odoo cleans up seed data removed from the manifest.
    cr.execute("""
        UPDATE ir_model_data SET noupdate = TRUE
         WHERE module = 'tangerine_address_base'
           AND ((model = 'res.country.ward' AND name ~ '^res_ward_[0-9]+$')
             OR (model = 'res.country.district' AND name ~ '^res_district_[0-9]+$'))
    """)
    # Earlier two-level releases marked even the official, versioned catalogue noupdate.
    cr.execute("""
        UPDATE ir_model_data SET noupdate = FALSE
         WHERE module = 'tangerine_address_base' AND model = 'res.country.ward'
           AND name ~ '^ward_vn_[0-9]+$'
    """)
