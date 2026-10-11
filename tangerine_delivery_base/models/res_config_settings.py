from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    webhook_log_retention_days = fields.Integer(
        string='Webhook Log Retention (days)',
        default=30,
        config_parameter='tangerine_delivery_base.webhook_log_retention_days',
        help='Automatically delete webhook logs older than this number of days. Set 0 to disable auto-delete.',
    )
