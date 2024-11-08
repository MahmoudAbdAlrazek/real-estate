from odoo import fields, models
from odoo.api import ondelete


class PropertyStateChangeReason(models.Model):
    _name = 'property.state.change.reason'
    _description = 'Reasons for changing property state'
    property_id = fields.Many2one(
            'property.items', string='Property',
            required=True,ondelete='cascade',readonly=True)

    change_reason = fields.Char(string='Reason', required=True)
    change_date = fields.Datetime(string='Change Date state', default=fields.Datetime.now,readonly=True)
    old_state = fields.Char(string='Old State', required=True,readonly=True)
    new_state = fields.Char(string='New State', required=True,readonly=True)


