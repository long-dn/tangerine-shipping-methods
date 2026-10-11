import json
from odoo import fields, models, api
from ..settings.constants import settings


class ChooseDeliveryCarrier(models.TransientModel):
    _inherit = 'choose.delivery.carrier'

    viettelpost_service_id = fields.Many2one('viettelpost.service', string='Service')
    viettelpost_service_extend_id = fields.Many2one('viettelpost.service.extend', string='Service Extend')
    viettelpost_national_type = fields.Selection(selection=settings.national_type.value, string='National Type')
    viettelpost_product_type = fields.Selection(selection=settings.product_type.value, string='Product Type')

    @api.onchange('carrier_id')
    def _onchange_viettelpost_provider(self):
        for rec in self:
            if rec.carrier_id and rec.carrier_id.delivery_type == settings.code.value:
                rec.viettelpost_product_type = rec.carrier_id.default_viettelpost_product_type
                rec.viettelpost_national_type = rec.carrier_id.default_viettelpost_national_type
                rec.viettelpost_service_id = rec.carrier_id.default_viettelpost_service_id
                rec.viettelpost_service_extend_id = rec.carrier_id.default_viettelpost_service_extend_id

    @api.onchange('viettelpost_service_id', 'viettelpost_service_extend_id',
                  'viettelpost_national_type', 'viettelpost_product_type')
    def _onchange_viettelpost_service_id(self):
        # the estimated cost depends on the chosen service
        if self.carrier_id.delivery_type == settings.code.value:
            self._handle_delivery_vals(self._get_carrier_delivery_rate(self.carrier_id))

    def _get_carrier_delivery_rate(self, carrier):
        if carrier.delivery_type == settings.code.value:
            wizard = self if carrier == self.carrier_id else self.browse()
            self = self.with_context(
                viettelpost_total_weight=self.total_weight,
                viettelpost_service_code=wizard.viettelpost_service_id.code or carrier.default_viettelpost_service_id.code or settings.default_service_type.value,
                viettelpost_service_extend_code=wizard.viettelpost_service_extend_id.code or carrier.default_viettelpost_service_extend_id.code or None,
                viettelpost_national_type=wizard.viettelpost_national_type or carrier.default_viettelpost_national_type or settings.default_national_type.value,
                viettelpost_product_type=wizard.viettelpost_product_type or carrier.default_viettelpost_product_type or settings.default_product_type.value,
            )
        return super()._get_carrier_delivery_rate(carrier)

    def button_confirm(self):
        if self.carrier_id.delivery_type == settings.code.value:
            viettelpost_quotation_data = json.dumps({
                'viettelpost_service_id': self.viettelpost_service_id.id,
                'viettelpost_service_extend_id': self.viettelpost_service_extend_id.id if self.viettelpost_service_extend_id else None,
                'viettelpost_national_type': self.viettelpost_national_type,
                'viettelpost_product_type': self.viettelpost_product_type,
                'viettelpost_cod': self.is_cod,
                'viettelpost_cod_amount': self.cod_amount
            })
            self = self.with_context(viettelpost_quotation_data=viettelpost_quotation_data)
        return super(ChooseDeliveryCarrier, self).button_confirm()
