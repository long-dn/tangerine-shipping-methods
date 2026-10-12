import json
from odoo import fields, models, api
from ..settings.constants import settings


class ChooseDeliveryCarrier(models.TransientModel):
    _inherit = 'choose.delivery.carrier'

    ahamove_service_id = fields.Many2one('ahamove.service', string='Service')
    ahamove_service_request_ids = fields.Many2many(
        'ahamove.service.request',
        'estimate_request_rel',
        'choose_id',
        'request_id',
        string='Request Type'
    )
    promo_code = fields.Char(string='Promotion Code')

    @api.onchange('carrier_id')
    def _onchange_ahamove_provider(self):
        for rec in self:
            if rec.carrier_id and rec.carrier_id.delivery_type == settings.ahamove_code.value:
                rec.ahamove_service_id = rec.carrier_id.default_ahamove_service_id
                rec.ahamove_service_request_ids = rec.carrier_id.default_ahamove_service_request_ids

    @api.onchange('ahamove_service_id', 'ahamove_service_request_ids', 'promo_code')
    def _onchange_ahamove_service_id(self):
        # the estimate depends on the service, its requests and the promotion
        if self.carrier_id.delivery_type == settings.ahamove_code.value:
            self._handle_delivery_vals(self._get_carrier_delivery_rate(self.carrier_id))

    def _get_carrier_delivery_rate(self, carrier):
        if carrier.delivery_type == settings.ahamove_code.value:
            if carrier == self.carrier_id and self.ahamove_service_id:
                service, requests = self.ahamove_service_id, self.ahamove_service_request_ids
            else:
                service, requests = carrier.default_ahamove_service_id, carrier.default_ahamove_service_request_ids
            self = self.with_context(
                ahamove_service=service.code,
                ahamove_service_request_ids=requests,
                promo_code=self.promo_code if carrier == self.carrier_id else False,
            )
        return super()._get_carrier_delivery_rate(carrier)

    def button_confirm(self):
        if self.carrier_id.delivery_type == settings.ahamove_code.value:
            self = self.with_context(ahamove_quotation_data=json.dumps({
                'ahamove_service_id': self.ahamove_service_id.id,
                'ahamove_service_request_ids': self.ahamove_service_request_ids.ids,
                'promo_code': self.promo_code,
                'ahamove_cod': self.is_cod,
                'ahamove_cod_amount': self.cod_amount
            }))
        return super(ChooseDeliveryCarrier, self).button_confirm()
