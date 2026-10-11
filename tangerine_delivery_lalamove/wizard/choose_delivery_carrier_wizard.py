from odoo import fields, models, api
from ..settings.constants import settings


class ChooseDeliveryCarrierLalamove(models.TransientModel):
    _inherit = 'choose.delivery.carrier'

    lalamove_service_id = fields.Many2one('lalamove.service', string='Vehicle Type')
    lalamove_special_service_ids = fields.Many2many(
        'lalamove.special.service',
        'lalamove_estimate_request_rel',
        'choose_id',
        'special_id',
        string='Service Type'
    )
    lalamove_quotation_data = fields.Json(string='Lalamove Quotation Data')

    @api.onchange('carrier_id')
    def _onchange_lalamove_provider(self):
        for rec in self:
            if rec.carrier_id and rec.carrier_id.delivery_type == settings.lalamove_code.value:
                rec.lalamove_service_id = rec.carrier_id.default_lalamove_service_id
                rec.lalamove_special_service_ids = rec.carrier_id.default_lalamove_special_service_ids

    @api.onchange('lalamove_service_id', 'lalamove_special_service_ids')
    def _onchange_lalamove_service_id(self):
        # the quotation depends on the vehicle and the special requests
        if self.carrier_id.delivery_type == settings.lalamove_code.value and self.lalamove_service_id:
            self._handle_delivery_vals(self._get_carrier_delivery_rate(self.carrier_id))

    def _lalamove_get_services(self, carrier):
        if carrier == self.carrier_id and self.lalamove_service_id:
            return self.lalamove_service_id, self.lalamove_special_service_ids
        return carrier.default_lalamove_service_id, carrier.default_lalamove_special_service_ids

    def _retrieve_delivery_rate(self):
        # Lalamove cannot quote without a vehicle: wait for the user to choose
        # one instead of failing as soon as the carrier is selected.
        if self.carrier_id.delivery_type == settings.lalamove_code.value \
                and not self._lalamove_get_services(self.carrier_id)[0]:
            self._set_delivery_vals({'delivery_message': False, 'delivery_price': 0.0, 'display_price': 0.0})
            return
        return super()._retrieve_delivery_rate()

    def _get_carrier_delivery_rate(self, carrier):
        if carrier.delivery_type == settings.lalamove_code.value:
            service, special_services = self._lalamove_get_services(carrier)
            self = self.with_context(
                llm_service=service.code,
                llm_special_service=special_services.mapped('code'),
                llm_package_weight=self.total_weight,
            )
        return super()._get_carrier_delivery_rate(carrier)

    def _set_delivery_vals(self, delivery_vals):
        super()._set_delivery_vals(delivery_vals)
        if 'display_price' in delivery_vals and self.carrier_id.delivery_type == settings.lalamove_code.value:
            self.lalamove_quotation_data = delivery_vals.get('no_rate') or False

    def button_confirm(self):
        if self.lalamove_quotation_data and self.carrier_id.delivery_type == settings.lalamove_code.value:
            self = self.with_context(llm_quotation_data=self.lalamove_quotation_data)
        return super(ChooseDeliveryCarrierLalamove, self).button_confirm()
