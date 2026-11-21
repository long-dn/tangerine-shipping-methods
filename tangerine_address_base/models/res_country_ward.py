from odoo import models, fields, api


class Ward(models.Model):
    _name = 'res.country.ward'
    _description = 'ward'
    _order = 'name'

    code = fields.Char(string='Ward Code')
    name = fields.Char(string='Ward name')
    slug = fields.Char(string='Ward 3L')
    slug2 = fields.Char(string='Ward 2L')
    district_id = fields.Many2one('res.country.district', string='District',
                                  domain="[('state_id', '=', state_id)]")
    state_id = fields.Many2one('res.country.state', 'State',
                               domain="[('country_id', '=', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', required=True, default=lambda self: self.env.ref('base.vn'))
    type = fields.Selection(selection=[
        ('0', 'Phường'),
        ('1', 'Xã'),
        ('2', 'Thị trấn'),
        ('3', 'Huyện')
    ], string='Type')

    active = fields.Boolean(default=True)
    ward_type = fields.Selection([
        ('ward', 'Ward'), ('commune', 'Commune'), ('special_zone', 'Special Zone'),
    ], string='Ward Type')

    def _vietnamese_address_name(self):
        if not self:
            return ''
        self.ensure_one()
        labels = {'ward': 'Phường', 'commune': 'Xã', 'special_zone': 'Đặc khu'}
        label = labels.get(self.ward_type)
        return '%s %s' % (label, self.name) if label and self.active else (self.name or '')

    @api.depends('name', 'ward_type', 'active')
    def _compute_display_name(self):
        for ward in self:
            ward.display_name = ward._vietnamese_address_name()
