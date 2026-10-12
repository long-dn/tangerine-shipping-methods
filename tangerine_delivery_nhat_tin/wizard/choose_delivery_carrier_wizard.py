import json
from odoo import fields, models, api
from ..settings.constants import settings


class ChooseDeliveryCarrier(models.TransientModel):
    _inherit = 'choose.delivery.carrier'

    ntl_service_type = fields.Selection(selection=settings.service_type.value, string='Service Type')
    ntl_payment_method = fields.Selection(selection=settings.payment_method.value, string='Payment Method')

    @api.onchange('carrier_id')
    def _onchange_nhat_tin_provider(self):
        for rec in self:
            if rec.carrier_id and rec.carrier_id.delivery_type == settings.nhat_tin_code.value:
                rec.ntl_service_type = rec.carrier_id.default_ntl_service_type
                rec.ntl_payment_method = rec.carrier_id.default_ntl_payment_method

    @api.onchange('ntl_service_type', 'ntl_payment_method', 'is_cod', 'cod_amount')
    def _onchange_nhat_tin_service_type(self):
        # the price depends on the service, the payment method and the cash on delivery
        if self.carrier_id.delivery_type == settings.nhat_tin_code.value:
            self._handle_delivery_vals(self._get_carrier_delivery_rate(self.carrier_id))

    def _get_carrier_delivery_rate(self, carrier):
        if carrier.delivery_type == settings.nhat_tin_code.value:
            wizard = self if carrier == self.carrier_id else self.browse()
            self = self.with_context(
                ntl_service_type=wizard.ntl_service_type or carrier.default_ntl_service_type or settings.default_service_type.value,
                ntl_payment_method=wizard.ntl_payment_method or carrier.default_ntl_payment_method or settings.default_payment_method.value,
                ntl_cod=wizard.is_cod,
                ntl_cod_amount=wizard.cod_amount,
                ntl_cargo_value=self.order_id.amount_total,
            )
        return super()._get_carrier_delivery_rate(carrier)

    def button_confirm(self):
        if self.carrier_id.delivery_type == settings.nhat_tin_code.value:
            self = self.with_context(ntl_quotation_data=json.dumps({
                'ntl_service_type': self.ntl_service_type,
                'ntl_payment_method': self.ntl_payment_method,
                'ntl_cod': self.is_cod,
                'ntl_cod_amount': self.cod_amount
            }))
        return super(ChooseDeliveryCarrier, self).button_confirm()
