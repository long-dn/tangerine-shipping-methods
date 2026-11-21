# -*- coding: utf-8 -*-
import json

import requests
from dataclasses import dataclass
from odoo import _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError
from odoo.addons.tangerine_delivery_base.settings.utils import (
    URLBuilder,
    datetime_to_rfc3339,
    standardization_e164
)
from odoo.addons.tangerine_delivery_base.api.connection import Connection
from ..settings.constants import settings


@dataclass
class Client:
    conn: Connection

    def _build_header(self):
        headers = json.loads(safe_eval(self.conn.endpoint.headers))
        if self.conn.endpoint.code in (settings.ntl_calculate_price_route_code.value,
                                       settings.ntl_create_bill_route_code.value):
            provider = self.conn.provider
            try:
                response = requests.post(
                    URLBuilder.builder(host=provider.domain, routes=['/v1/auth/sign-in']),
                    json={'username': provider.username, 'password': provider.password},
                    timeout=15,
                )
                response.raise_for_status()
                token = (response.json().get('data') or {}).get('jwt_token')
            except (requests.RequestException, ValueError) as exc:
                raise UserError(_('Nhất Tín authentication failed. Check the API account.')) from exc
            if not token:
                raise UserError(_('Nhất Tín did not return an access token.'))
            headers['Authorization'] = 'Bearer ' + token
        elif self.conn.endpoint.is_need_access_token:
            headers['username'] = self.conn.provider.username
            headers['password'] = self.conn.provider.password
        return headers

    @staticmethod
    def _validate_response(result):
        if not result.get('success'):
            raise UserError(_(f'{result.get("message")}'))
        return result

    def _execute(self, payload=None, path_parameter=None):
        if self.conn.endpoint.code == settings.ntl_print_bill_route_code.value:
            return URLBuilder.builder(
                host=self.conn.provider.domain_printer,
                routes=[self.conn.endpoint.route.format(
                    bill_code=path_parameter,
                    partner_id=self.conn.provider.ntl_partner_id
                )]
            )
        return self._validate_response(
            self.conn.execute_restful(
                url=URLBuilder.builder(
                    host=self.conn.provider.domain,
                    routes=[self.conn.endpoint.route]
                ),
                headers=self._build_header(),
                method=self.conn.endpoint.method,
                **payload or {}
            )
        )

    def calculate_price(self, payload): return self._execute(payload=payload)

    def create_bill(self, payload): return self._execute(payload=payload)

    def cancel_bill(self, payload): self._execute(payload=payload)

    def print_bill(self, carrier_tracking_ref): return self._execute(path_parameter=carrier_tracking_ref)
