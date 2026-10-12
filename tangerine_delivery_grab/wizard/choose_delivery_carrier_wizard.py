import json
from odoo import fields, models, api
from ..settings.constants import settings


class ChooseDeliveryCarrier(models.TransientModel):
    _inherit = 'choose.delivery.carrier'

    grab_service_type = fields.Selection(selection=settings.service_type.value, string='Service Type')
    grab_vehicle_type = fields.Selection(selection=settings.vehicle_type.value, string='Vehicle Type')

    @api.onchange('carrier_id')
    def _onchange_grab_provider(self):
        for rec in self:
            if rec.carrier_id and rec.carrier_id.delivery_type == settings.grab_code.value:
                rec.grab_service_type = rec.carrier_id.default_grab_service_type
                rec.grab_vehicle_type = rec.carrier_id.default_grab_vehicle_type

    @api.onchange('grab_service_type', 'grab_vehicle_type', 'is_cod', 'cod_amount')
    def _onchange_grab_service_type(self):
        # the quote depends on the service, the vehicle and the cash on delivery
        if self.carrier_id.delivery_type == settings.grab_code.value:
            self._handle_delivery_vals(self._get_carrier_delivery_rate(self.carrier_id))

    def _get_carrier_delivery_rate(self, carrier):
        if carrier.delivery_type == settings.grab_code.value:
            wizard = self if carrier == self.carrier_id else self.browse()
            self = self.with_context(
                grab_service_type=wizard.grab_service_type or carrier.default_grab_service_type or settings.default_service_type.value,
                grab_vehicle_type=wizard.grab_vehicle_type or carrier.default_grab_vehicle_type or settings.default_vehicle_type.value,
                grab_cod=wizard.is_cod,
                grab_cod_amount=wizard.cod_amount,
            )
        return super()._get_carrier_delivery_rate(carrier)

    def button_confirm(self):
        if self.carrier_id.delivery_type == settings.grab_code.value:
            self = self.with_context(grab_quotation_data=json.dumps({
                'grab_service_type': self.grab_service_type,
                'grab_vehicle_type': self.grab_vehicle_type,
                'grab_cod': self.is_cod,
                'grab_cod_amount': self.cod_amount
            }))
        return super(ChooseDeliveryCarrier, self).button_confirm()
