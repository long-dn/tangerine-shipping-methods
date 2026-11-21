from odoo import _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

from .main import validate_ward


class PortalAddress(CustomerPortal):

    MANDATORY_BILLING_FIELDS = [f for f in CustomerPortal.MANDATORY_BILLING_FIELDS if f != 'city']
    OPTIONAL_BILLING_FIELDS = CustomerPortal.OPTIONAL_BILLING_FIELDS + ['city', 'ward_id']

    def details_form_validate(self, data, *args, **kwargs):
        errors, messages = super().details_form_validate(data, *args, **kwargs)
        if not data.get('city') and str(data.get('country_id')) != str(request.env.ref('base.vn').id):
            errors['city'] = 'missing'
            messages.append(_('Enter the city.'))
        validate_ward(data, errors, messages)
        return errors, messages
