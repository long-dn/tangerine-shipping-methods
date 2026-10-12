from odoo import fields, models, api
from ..settings.constants import settings


class ChooseDeliveryCarrier(models.TransientModel):
    _inherit = 'choose.delivery.carrier'

    express_247_service_type_id = fields.Many2one('service.type.247.express', string='Service Type')

    @api.onchange('carrier_id')
    def _onchange_express_247_provider(self):
        for rec in self:
            if rec.carrier_id and rec.carrier_id.delivery_type == settings.code.value:
                rec.express_247_service_type_id = rec.carrier_id.default_express_247_service_type_id

    @api.onchange('express_247_service_type_id')
    def _onchange_express_247_service_type_id(self):
        # the price depends on the service type
        if self.carrier_id.delivery_type == settings.code.value:
            self._handle_delivery_vals(self._get_carrier_delivery_rate(self.carrier_id))

    def _get_carrier_delivery_rate(self, carrier):
        if carrier.delivery_type == settings.code.value:
            wizard = self if carrier == self.carrier_id else self.browse()
            self = self.with_context(
                express_247_service_type=wizard.express_247_service_type_id.code or carrier.default_express_247_service_type_id.code or settings.default_service_type.value,
            )
        return super()._get_carrier_delivery_rate(carrier)
