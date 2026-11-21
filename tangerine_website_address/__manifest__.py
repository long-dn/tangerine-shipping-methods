# -*- coding: utf-8 -*-
{
    'name': 'Vietnam Wards on Website',
    'summary': 'Select a Vietnamese ward by province at checkout and on the customer portal.',
    'author': 'Long Duong Nhat',
    'website': 'https://github.com/long-dn',
    'license': 'LGPL-3',
    'category': 'Extra Tools',
    'version': '15.0.3.0.0',
    'support': 'odoo.tangerine@gmail.com',

    'depends': ['website_sale', 'tangerine_address_base'],
    'data': ['views/templates.xml'],
    'installable': True,
    'assets': {'web.assets_frontend': ['tangerine_website_address/static/src/js/vietnam_ward.js']},
}
